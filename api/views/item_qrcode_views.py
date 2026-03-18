import io
import base64
from drf_spectacular.utils import extend_schema

import qrcode
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Item
from api.serializers.item_qrcode_serializer import (
    QRCodeGenerateSerializer,
    QRCodeResponseSerializer,
    ItemVerifySerializer,
)

@extend_schema(
    request=QRCodeGenerateSerializer,
    responses=QRCodeResponseSerializer,
)
class QRCodeGenerateView(APIView):
    """
    Generate a QR code PNG and send it back to the front end in base64 format.
    The front end is responsible for displaying/printing it and then affixing it to the item.
    """

    def post(self, request):
        serializer = QRCodeGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data["item_id"]

        if not Item.objects.filter(id=item_id).exists():
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # The QR code contains a verify URL
        # After scanning, your phone will open this URL, 
        # and your front-end or back-end will then display the item information.
        base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
        qr_url = f"{base_url}/items/{item_id}/verify"

        # QR Code image（PNG → base64）
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response_data = {
            "item_id": str(item_id),
            "qr_image_base64": img_base64,
            "qr_url": qr_url,
        }
        return Response(
            QRCodeResponseSerializer(response_data).data,
            status=status.HTTP_200_OK,
        )


class QRCodeVerifyView(APIView):
    """
    The URL opened after scanning the QR code sends back detailed item information.
    """

    def get(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItemVerifySerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)