from rest_framework import permissions


class IsAuthenticatedAndReadOnly(permissions.BasePermission):
    """Права - только чтение для авторизированных пользователей.
    Наследуется от BasePermission
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                and request.user.is_authenticated)
