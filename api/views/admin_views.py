from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Item
from api.serializers import ItemSerializer
from rest_framework.views import APIView
from rest_framework import generics, permissions


class AuditQueueView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Item.objects.filter(status="pending")


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


# Reject Post APi
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

        return Response({"message": "Post rejected", "reason": reason}, status=200)


# Admin Delete Post API
class AdminDeletePostView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()

        return Response({"message": "Post deleted"}, status=200)


# Admin Edit Post API
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
