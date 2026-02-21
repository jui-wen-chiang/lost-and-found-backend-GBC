from rest_framework import generics, permissions
from .models import Item, Category, Location
from .serializers import ItemSerializer, CategorySerializer, LocationSerializer

# -------- Health Check --------
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def health(request):
    return Response({"status": "healthy"})


# -------- Categories & Locations (Read-only) --------

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


# -------- Item CRUD --------

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