from rest_framework import serializers
from api.models import Item

class QRCodeGenerateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()


class QRCodeResponseSerializer(serializers.Serializer):
    """Response: Send a QR code image (base64) to the frontend."""
    item_id = serializers.IntegerField()
    qr_image_base64 = serializers.CharField()   # PNG base64 string
    qr_url = serializers.CharField()            # URL encoded into QR code


class ItemVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Item 
        fields = "__all__"