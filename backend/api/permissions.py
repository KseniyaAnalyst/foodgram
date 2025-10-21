# from rest_framework.permissions import (
#     SAFE_METHODS, BasePermission)


# class IsAuthorOrReadOnly(BasePermission):

#     def has_object_permission(self, request, view, instance):
#         if request.method in SAFE_METHODS:
#             return True
#         return getattr(
#             instance, 'author_id', None) == getattr(
#                 request.user, 'id', None)

# backend/api/permissions.py

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
