from rest_framework import serializers
from api.models import Item
from .image_serializers import ImageSerializer

class ItemSerializer(serializers.ModelSerializer):
    # Nested read-only images; write is handled separately via image_service
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ["owner", "created_at", "updated_at"]