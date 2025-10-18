from rest_framework.permissions import (
    SAFE_METHODS, BasePermission)


class IsAuthorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, instance):
        if request.method in SAFE_METHODS:
            return True
        return getattr(
            instance, 'author_id', None) == getattr(
                request.user, 'id', None)
