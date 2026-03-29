from django.db import transaction
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser

from api.models import Item, Image
from api.serializers import ItemSerializer, ImageSerializer
from api.utils import ItemFilter
from api.services import image_service


class ItemListCreateView(generics.ListCreateAPIView):
    """
    Create item + images: 
        POST /api/items/ with FormData (fields: name, description, images[],...)
    """
    queryset = Item.objects.prefetch_related("images").all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemFilter

    @extend_schema(
        operation_id="create_item",
        request={
            "multipart/form-data": ItemSerializer
        },
    )        
    def create(self, request, *args, **kwargs):
        """
        Item Create Flow:
        1. View initialize serializer and parse multipart request
        2. Validate data via Serializer (triggers service-level image validation)
        3. Persist item and process image attachments via Service layer
        
        Response: Return the newly created item with prefetched image records
        """
        serializer = self.get_serializer(data=request.data)
        # is_valid() triggers validate_upload_images
        serializer.is_valid(raise_exception=True)

        # triggers Serializer.create
        item = serializer.save(owner=request.user)

        return Response(
            self.get_serializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.prefetch_related("images").all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def _check_owner(self, item):
        user = self.request.user
        if user != item.owner and not (user.is_staff or getattr(user, 'role', '') == 'admin'):
            raise PermissionDenied("Not your item.")

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        self._check_owner(item)

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(item, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        files = request.FILES.getlist("upload_images")
        keep_ids = request.data.getlist("existing_image_ids")
        keep_ids = [int(i) for i in keep_ids if str(i).isdigit()]

        with transaction.atomic():
            updated_item = serializer.save()

            # Delete images that the user removed in the UI
            if keep_ids is not None or files:
                existing_images = Image.objects.filter(item=updated_item)
                to_delete = existing_images.exclude(id__in=keep_ids)
                for img in to_delete:
                    image_service.delete_from_storage(img.file_path)
                to_delete.delete()

            # Upload any new images
            if files:
                image_service.process_images(updated_item, files)

        updated_item.refresh_from_db()
        return Response(ItemSerializer(updated_item).data)

    def perform_destroy(self, instance):
        self._check_owner(instance)
        from api.models import Claim
        if Claim.objects.filter(item=instance).exclude(status="rejected").exists():
            raise PermissionDenied("Cannot delete an item that has active claims.")
        # Image files are deleted here; DB cascade handles the records
        image_service.delete_images_by_item(instance)
        instance.delete()


class ImageListCreateView(APIView):
    """
    GET  /items/<item_id>/images/        → list images for an item
    POST /items/<item_id>/images/        → add images to an existing item
    """

    permission_classes = [permissions.IsAuthenticated]

    def _get_item(self, item_id, user):
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return None, Response(
                {"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if item.owner != user:
            return None, Response(
                {"detail": "Not your item."}, status=status.HTTP_403_FORBIDDEN
            )
        return item, None

    def get(self, request, item_id):
        item, error = self._get_item(item_id, request.user)
        if error:
            return error
        images = Image.objects.filter(item=item)
        return Response(ImageSerializer(images, many=True).data)

    def post(self, request, item_id):
        item, error = self._get_item(item_id, request.user)
        if error:
            return error

        files = request.FILES.getlist("images")
        if not files:
            return Response(
                {"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            saved = image_service.process_images(item, files)

        return Response(
            ImageSerializer(saved, many=True).data, status=status.HTTP_201_CREATED
        )


class ImageDetailView(APIView):
    """
    PATCH  /items/<item_id>/images/<image_id>/   → set as primary
    DELETE /items/<item_id>/images/<image_id>/   → delete single image
    """

    permission_classes = [permissions.IsAuthenticated]

    def _get_image(self, item_id, image_id, user):
        try:
            image = Image.objects.select_related("item").get(
                pk=image_id, item_id=item_id
            )
        except Image.DoesNotExist:
            return None, Response(
                {"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if image.item.owner != user:
            return None, Response(
                {"detail": "Not your item."}, status=status.HTTP_403_FORBIDDEN
            )
        return image, None

    def patch(self, request, item_id, image_id):
        """Set this image as primary (clears others)."""
        image, error = self._get_image(item_id, image_id, request.user)
        if error:
            return error

        with transaction.atomic():
            Image.objects.filter(item_id=item_id).update(is_primary=False)
            image.is_primary = True
            image.save(update_fields=["is_primary"])

        return Response(ImageSerializer(image).data)

    def delete(self, request, item_id, image_id):
        image, error = self._get_image(item_id, image_id, request.user)
        if error:
            return error

        image_service.delete_from_storage(image.file_path)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LostItemsReportView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.filter(item_type="lost")


class FoundItemsReportView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.filter(item_type="found")


class ItemStatusStatsView(APIView):
    def get(self, request):
        stats = (
            Item.objects
            .values("status")
            .annotate(count=Count("id"))
        )

        result = {s["status"]: s["count"] for s in stats}
        return Response(result)
