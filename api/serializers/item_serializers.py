from rest_framework import serializers
from .image_serializers import ImageSerializer
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from django.db import transaction
from api.models import Item
from api.services import image_service
from api.models import Item, Category, Location

class ItemSerializer(serializers.ModelSerializer):
    # GET images list
    images = ImageSerializer(many=True, read_only=True)
    
    # Upload images via POST 
    upload_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Item
        fields = [
            "id", "title", "description", "item_type", "status",
            "lost_at", "found_at", "category", "location",
            "owner", "created_at", "updated_at",
            "images", "upload_images", "url"
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_url(self, obj):
        return image_service.get_image_url(obj.file_path)
    
    def validate_upload_images(self, value):
        if value:
            image_service.validate_image_count(value)
            for img in value:
                image_service.validate_image(img)
        return value

    def create(self, validated_data):
        # avoid Item.objects.create error
        upload_images = validated_data.pop('upload_images', [])
        
        # Ensure both the Item and Image succeed.
        with transaction.atomic():
            item = Item.objects.create(**validated_data)
            
            # The Service is responsible for entity archiving and database records.
            if upload_images:
                image_service.process_images(item, upload_images)
                
        return item

    def update(self, instance, validated_data):
        # Remove upload_images so default update doesn't try to set it on the model
        validated_data.pop('upload_images', None)
        return super().update(instance, validated_data)

    # Swagger display fix
    @extend_schema_field(OpenApiTypes.BINARY)
    def get_upload_images(self, obj):
        return None