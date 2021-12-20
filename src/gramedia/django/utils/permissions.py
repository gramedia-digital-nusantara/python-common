from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Owners of object or Admin
    TODO : Do check also for Admin user to allow permissions
    """

    def has_object_permission(self, request, view, obj):
        if request.user and (request.user.is_staff or request.user.is_superuser) and request.user.is_active:
            return True
        return False


class IsReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
        )
