from rest_framework import permissions


class AuthorOrReadPermission(permissions.BasePermission):
    """Автор или только чтение.
    Наследование от базового класса разрешений.
    Определяется правило что доступ к представлению объекта только
    для авторизированных пользователей или если запрос
    в списке безопасных методов.
    Список методов входящих в безопасные не изменялся.
    Доступ к объекту только если запрос в списке безопасных методов
    или если доступ запрошен автором объекта.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Админ или только чтение.
    Доступ к представлению только если метод в списке безопасных
    или пользователь имеет статус Админ.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser)))
