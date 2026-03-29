from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly


class IsAppAdmin(permissions.BasePermission):
    """
    Allow access only to users whose role is 'admin'.
    Unlike IsAdminUser, this checks the app-level role field
    instead of Django's is_staff flag.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    The owner of the item can edit it, while others can only read it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class RoleBasedPermission(permissions.BasePermission):
    """
    Restricts access based on the allowed_roles defined on the view.

    Unauthenticated users are always denied.
    If the view does not define allowed_roles, all authenticated users are granted access.

    Usage:
        class MyView(APIView):
            permission_classes = [RoleBasedPermission]
            allowed_roles = ["staff", "admin"]
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        allowed_roles = getattr(view, "allowed_roles", [])
        if not allowed_roles:
            return True

        return request.user.role in allowed_roles

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)