from djoser.serializers import UserSerializer
from recipes.models import Follow
from rest_framework import serializers
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Пользовательский сериализатор для пользователя.
    Наследуется от UserSerializer.

    Returns:
        obj (User): возвращает пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Получения значения поля подписки.
        Есть ли пользователь в избранномс или нет.

        Args:
            obj (User): объект пользователя к которому обращается запрос.

        Returns:
            bool: есть ли у пользователя отправившего запрос пользователь в
            списке избранного.
        """
        user = self.context['request'].user.id
        request_profile = obj.id
        if user == request_profile:
            return False
        return Follow.objects.filter(user_id=user,
                                     following_id=request_profile).exists()
