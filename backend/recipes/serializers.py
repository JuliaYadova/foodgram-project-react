from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from users.models import User
from users.serializers import CustomUserSerializer

from .models import (Favourites, Ingredient, IngredientForRecipe, Recipe,
                     Shopping_cart, Tag)


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        import base64
        import uuid

        import six
        from django.core.files.base import ContentFile

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = '%s.%s' % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension

        return extension


class TagPOSTSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        id = data
        tag = get_object_or_404(Tag, pk=id)
        return tag

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug',)
        extra_kwargs = {
            'slug': {'read_only': True},
            'name': {'read_only': True},
            'color': {'read_only': True},
        }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientPOSTSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    def to_internal_value(self, data):
        ingredient_pk = data.get('id')
        internal_data = super().to_internal_value(data)
        ingredient = get_object_or_404(Ingredient, pk=ingredient_pk)
        internal_data['ingridient'] = ingredient
        return internal_data

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        extra_kwargs = {
            'name': {'read_only': True},
            'measurement_unit': {'read_only': True},
        }

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipePOSTSerializer(serializers.ModelSerializer):
    ingredients = IngredientPOSTSerializer(many=True,
                                           source='recipe_for_ingridient')
    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagPOSTSerializer(many=True)

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

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_for_ingridient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = ingredient['ingridient']
            IngredientForRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author', instance.author)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('recipe_for_ingridient')
        IngredientForRecipe.objects.filter(recipe_id=instance.id).delete()
        for ingredient in ingredients:
            current_ingredient = ingredient['ingridient']
            IngredientForRecipe.objects.create(
                ingredient=current_ingredient,
                recipe_id=instance.id,
                amount=ingredient['amount'])
        instance.save()
        return instance

    def validate_cooking_time(self, value):
        min_time = 1
        if (value < min_time):
            raise serializers.ValidationError(
                f'Время приготовления должно быть больше {min_time} мин.!'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientPOSTSerializer(read_only=True,
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
        user = self.context['request'].user.id
        recipe = obj.id
        if Favourites.objects.filter(user_id=user,
                                     recipe_id=recipe).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user.id
        recipe = obj.id
        if Shopping_cart.objects.filter(user_id=user,
                                        recipe_id=recipe).exists():
            return True
        return False


class RecipeGETShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)


class UserFollowSerializer(CustomUserSerializer):

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
