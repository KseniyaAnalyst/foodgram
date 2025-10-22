from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return obj.author == user or user.is_staff or user.is_superuser
