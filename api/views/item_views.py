from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Item
from api.serializers import ItemSerializer
from api.utils import ItemFilter

class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemFilter

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