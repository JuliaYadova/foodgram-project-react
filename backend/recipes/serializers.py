from recipes.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, IngredientForRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import User
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для списка ингридиентов со всеми полями модели Ingredient.
    Наследуется от ModelSerializer.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов для модели IngredientForRecipe.
    Наследуется от ModelSerializer.

    Для связи с таблицей Ingredient настроены поля:
    id (int): id ингридиента в таблице ингридиентов. Только чтение.
    name (str): название ингридиента в таблице ингридиентов. Только чтение.
    measurement_unit (str): единица измерения в таблице ингридиентов.
    Только чтение.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для списка тэгов со всеми полями модели Tag.
    Наследуется от ModelSerializer.
    """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientPOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов при создании/редактировании рецепта.
    Наследуется от ModelSerializer.

    Настраиваемые поля:
    id (int): связанное значение, список объектов модели Ingredient.
    amount (int): количество ингридиента.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов.
    Наследуется от ModelSerializer.

    Настраиваемые поля:
    ingredients (serializer): вложенный сериализатор IngredientPOSTSerializer,
    добавление нескольких элементов разрешено, ресурс связанная таблица.
    image (image): пользовательское поле для конвертации из base64 в
    изображение.
    author (serializer): вложенный сериализатор CustomUserSerializer.
    tags (queryset): поле связанной таблицы, добавление нескольких элементов
    разрешено.

    Raises:
        serializers.ValidationError: должен быть хотябы один ингридиент в
        рецепте.
        serializers.ValidationError: ингридиент не может повторяться.
        serializers.ValidationError: значение количества ингридиента больше
        нуля.
        serializers.ValidationError: должен быть выбран хотябы один тэг.
        serializers.ValidationError: тэг не может повторяться.
        serializers.ValidationError: время приготовления не может быть меньше
        параметра min_time.

    Returns:
        obj (Recipe): после записи рецепта возвращает созданный объект.
    """
    ingredients = IngredientPOSTSerializer(many=True,
                                           source='recipe_for_ingridient')
    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'image',
                  'name',
                  'text',
                  'cooking_time', )
        model = Recipe
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def validate(self, data):
        """Валидация ингридиентов и тэгов при создании/редактировании рецепта.

        Args:
            data (dict): данные для проверки (входные данные от пользователя)

        Raises:
            serializers.ValidationError: должен быть хотябы один ингридиент в
            рецепте.
            serializers.ValidationError: ингридиент не может повторяться.
            serializers.ValidationError: значение количества ингридиента больше
            нуля.
            serializers.ValidationError: должен быть выбран хотябы один тэг.
            serializers.ValidationError: тэг не может повторяться.

        Returns:
            data (dict): данные после проверки.
        """
        ingredients = data.get('recipe_for_ingridient')
        if not ingredients:
            raise serializers.ValidationError({
                'errors': 'Выберите хотя бы один ингредиент!'
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_obj = ingredient['id']
            if ingredient_obj in ingredients_list:
                raise serializers.ValidationError({
                    'errors': 'Ингредиент не должен повторяться!'
                })
            ingredients_list.append(ingredient_obj)
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError({
                    'errors': 'Количество ингридиента должно быть больше нуля.'
                })

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'errors': 'Выберите хотя бы один тэг!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'errors': 'Тэг не должен повторяться!'
                })
            tags_list.append(tag)
        return data

    def to_representation(self, instance):
        """Изменение представления после записи/редактирования объекта.

        Returns:
            obj (Recipe): возвращает сериализованный объект для представления.
            Используется другой сериализатор для чтения - RecipeSerializer.
        """
        return RecipeSerializer(instance, context=self.context).data

    def create_ingredients(self, ingredients, recipe):
        """Создание в базе данных в связанной таблице ингридиента в привязке к
        рецепту с указанием количества и создание связи рецепта и тэгов.

        Args:
            ingredients (dict): список ингридиентов.
            recipe (obj): объект Recipe который создается/редактируется.
        """
        IngredientForRecipe.objects.bulk_create(
            [
                IngredientForRecipe(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Создание рецепта.

        Args:
            validated_data (dict): полученные данные для создания рецепта от
            пользователя.

        Returns:
            obj (Recipe): созданный рецепт.
        """
        ingredients = validated_data.pop('recipe_for_ingridient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Редактируем созданный ранее рецепт.

        Args:
            instance (obj): изменяемый объект.
            validated_data (dict): измененные данные.

        Returns:
            obj (Recipe): изменный рецепт.
        """
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('recipe_for_ingridient')
        IngredientForRecipe.objects.filter(recipe_id=instance.id).delete()
        self.create_ingredients(ingredients, instance)
        super().update(instance, validated_data)
        return instance

    def validate_cooking_time(self, value):
        """Валидация времени приготоваления.
        Минимальное время задается внутри функции.

        Args:
            value (int): время приготовления указанное пользователем.

        Raises:
            serializers.ValidationError: время приготовления не может быть
            меньше параметра min_time.

        Returns:
            value (int): проверенное значение.
        """
        min_time = 1
        if (value < min_time):
            raise serializers.ValidationError(
                f'Время приготовления должно быть больше {min_time} мин.!'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта при чтении.
    Наследуется от ModelSerializer.
    Настраиваемые поля:
    ingredients (serializer): вложенный сериализатор
    IngredientForRecipeSerializer, вызов нескольких элементов разрешен, ресурс
    связанная таблица, только чтение.
    author (serializer): вложенный сериализатор CustomUserSerializer, только
    чтение.
    tags (serializer): вложенный сериализатор TagSerializer, добавление
    нескольких элементов разрешено.
    is_favorited (bool): проврка на добавленность в избранное пользователя.
    is_in_shopping_cart (bool): проврка на добавленность в корзину
    пользователя.
    """
    ingredients = IngredientForRecipeSerializer(read_only=True,
                                                many=True,
                                                source='recipe_for_ingridient')
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',)

    def get_is_favorited(self, obj):
        """Проверка на добавленность в избранное пользователя.

        Args:
            obj (Recipe): объект сериализации, рецепт.

        Returns:
            bool: возвращает значение есть ли рецепт в избранном.
        """
        user = self.context['request'].user.id
        recipe = obj.id
        return Favourite.objects.filter(user_id=user,
                                        recipe_id=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка на добавленность в список покупок пользователя.

        Args:
            obj (Recipe): объект сериализации, рецепт.

        Returns:
            bool: возвращает значение есть ли рецепт в списке.
        """
        user = self.context['request'].user.id
        recipe = obj.id
        return ShoppingCart.objects.filter(user_id=user,
                                           recipe_id=recipe).exists()


class RecipeGETShortSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта для сокращенного представления.
    Наследуется от ModelSerializer.
    """

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)


class UserFollowSerializer(CustomUserSerializer):
    """Сериализатор для представления списка избранных авторов.
    Наследуется от ModelSerializer.
    Настраиваемые поля:
    recipes (serializer): только чтение, ресурс связанная таблица, допускается
    несколько объектов.
    recipes_count (int): только чтение, по умолчанию ноль.
    """

    recipes = RecipeGETShortSerializer(many=True,
                                       read_only=True,
                                       source='recipe_set')
    recipes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
