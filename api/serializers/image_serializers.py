from rest_framework import serializers
from api.models import Image
from api.services import image_service

class ImageSerializer(serializers.ModelSerializer):
    file_path = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()  # ← 新增

    class Meta:
        model = Image
        fields = ["id", "file_path", "original_filename", "is_primary", "uploaded_at", "url"]
        read_only_fields = ["id", "file_path", "uploaded_at"]

    def get_url(self, obj):
        return image_service.get_image_url(obj.file_path)