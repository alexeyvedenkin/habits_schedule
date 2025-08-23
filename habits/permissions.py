from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение, позволяющее владельцу объекта выполнять действие"""

    def has_object_permission(self, request, view, obj):
        # Проверяем, является ли текущий пользователь владельцем привычки
        return obj.owner == request.user
