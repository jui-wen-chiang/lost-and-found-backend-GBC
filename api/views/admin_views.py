from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Item, User
from api.serializers import ItemSerializer
from api.permissions.rbac import IsAppAdmin


class AuditQueueView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAppAdmin]

    def get_queryset(self):
        return Item.objects.filter(status="pending")


class ApprovePostView(APIView):
    permission_classes = [IsAppAdmin]

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
    permission_classes = [IsAppAdmin]

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
    permission_classes = [IsAppAdmin]

    def delete(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()

        return Response({"message": "Post deleted"}, status=200)


# Admin Edit Post API
class AdminEditPostView(APIView):
    permission_classes = [IsAppAdmin]

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


class AdminUserListView(APIView):
    permission_classes = [IsAppAdmin]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")
        data = [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "date_joined": u.date_joined.isoformat() if u.date_joined else None,
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in users
        ]
        return Response(data)


class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAppAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        new_role = request.data.get("role")
        if new_role not in ("student", "staff", "admin"):
            return Response({"error": "Invalid role"}, status=400)

        user.role = new_role
        if new_role == "admin":
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()

        return Response({"message": f"Role updated to {new_role}", "role": user.role})


class VerifiedItemsListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAppAdmin]

    def get_queryset(self):
        return Item.objects.exclude(status="pending").order_by("-updated_at")
