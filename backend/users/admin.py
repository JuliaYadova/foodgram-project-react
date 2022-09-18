from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    """Пользователи.
    Наследуется от UserAdmin.
    Настроены поля фильтрации.
    """
    list_filter = ('username', 'email',)


admin.site.register(User, UserAdmin)
