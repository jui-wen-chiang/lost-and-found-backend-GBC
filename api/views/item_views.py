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