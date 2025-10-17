from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает изменять/удалять объект только его автору.
    Для безопасных методов (GET/HEAD/OPTIONS) — доступ всем.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(
            obj, "author_id", None) == getattr(
                request.user, "id", None)
