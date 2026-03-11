from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Count
from api.models import Item, Category, Location
from api.serializers.item_serializers import (
    ItemSerializer,
    CategorySerializer,
    LocationSerializer
)
# -------- Health --------
def health(request):
    return JsonResponse({"status": "ok"})


# -------- Categories --------
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# -------- Locations --------
class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer




class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user != self.get_object().owner:
            raise permissions.PermissionDenied("Not your item")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.owner:
            raise permissions.PermissionDenied("Not your item")
        instance.delete()



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

# -------- Admin Audit Queue --------

class AuditQueueView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Item.objects.filter(status="pending")
    

from rest_framework import status
from rest_framework.response import Response


class ApprovePostView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.status = "approved"
        item.save()

        return Response({"message": "Post approved"}, status=200)
    

#Reject Post APi    
class RejectPostView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        reason = request.data.get("reason", "")

        item.status = "rejected"
        item.save()

        return Response({
            "message": "Post rejected",
            "reason": reason
        }, status=200)

#Admin Delete Post API
class AdminDeletePostView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()

        return Response({"message": "Post deleted"}, status=200)
    
 #Admin Edit Post API   
class AdminEditPostView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        serializer = ItemSerializer(item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)