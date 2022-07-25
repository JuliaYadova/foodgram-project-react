from django.db.models import Count
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from recipes.filters import RecipeFilter
from recipes.models import (Favourites, Follow, Ingredient,
                            IngredientForRecipe, Recipe, Shopping_cart, Tag)
from recipes.paginator import LimitPageNumberPagination
from recipes.permissions import AuthorOrReadPermission
from recipes.serializers import (IngredientSerializer,
                                 RecipeGETShortSerializer,
                                 RecipePOSTSerializer, RecipeSerializer,
                                 TagSerializer, UserFollowSerializer)
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrReadPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipePOSTSerializer

    def get_permissions(self):
        if self.action not in ('list', 'retrieve'):
            return super().get_permissions()
        return (AllowAny(),)


class FavoritesOrShopingViewSet(viewsets.ModelViewSet):
    @action(
        detail=True,
        methods=(
            'post',
            'delete'
        ),
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            if not Favourites.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                Favourites.objects.create(
                    user=self.request.user,
                    recipe=recipe)
                favorite = Recipe.objects.get(id=pk)
                serializer = RecipeGETShortSerializer(favorite)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            text = 'errors: Объект уже в избранном.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            if Favourites.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                Favourites.objects.filter(
                    user=self.request.user,
                    recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            text = 'errors: Объект не в избранном.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=(
            'post',
            'delete'
        ),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            if not Shopping_cart.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                Shopping_cart.objects.create(
                    user=self.request.user,
                    recipe=recipe)
                recipe_in_list = Recipe.objects.get(id=pk)
                serializer = RecipeGETShortSerializer(recipe_in_list)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            text = 'errors: Объект уже в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            if Shopping_cart.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                recipe_in_list = get_object_or_404(Shopping_cart,
                                                   user=self.request.user,
                                                   recipe=recipe)
                recipe_in_list.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            text = 'errors: Объект не в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    filterset_fields = ('name',)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class FollowViewSet(viewsets.ModelViewSet):

    @action(
        detail=True,
        methods=(
            'post',
            'delete'
        ),
    )
    def subscribe(self, request, pk=None):
        if request.method == 'POST':
            following = get_object_or_404(User, id=pk)
            if following == self.request.user:
                text = 'errors: Нельзя подписаться на самого себя.'
                return Response(text, status=status.HTTP_400_BAD_REQUEST)
            if not Follow.objects.filter(
                    user=self.request.user,
                    following=following).exists():
                Follow.objects.create(
                    user=self.request.user,
                    following=following)
                follow = User.objects.filter(id=pk).annotate(
                    recipes_count=Count('recipe'))
                serializer = UserFollowSerializer(follow,
                                                  context={'request': request},
                                                  many=True)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            text = 'errors: Объект уже в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            following = get_object_or_404(User, id=pk)
            if Follow.objects.filter(
                    user=self.request.user,
                    following=following).exists():
                Follow.objects.filter(
                    user=self.request.user,
                    following=following).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            text = 'errors: Объект не в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    recipes = Recipe.objects.filter(shopping_cart__user=request.user)
    if recipes is None:
        text = 'errors: Список пуст.'
        return Response(text, status=status.HTTP_400_BAD_REQUEST)
    ingredients = {}
    for i in recipes:
        ingredient = IngredientForRecipe.objects.filter(recipe_id=i.id)
        for i in ingredient:
            ingredient_id = i.ingredient.id
            ingredient_amount = i.amount
            if ingredient_id in ingredients.keys():
                amout = ingredients[ingredient_id]
                amount_new = amout + ingredient_amount
                ingredients[ingredient_id] = amount_new
            else:
                ingredients[ingredient_id] = ingredient_amount
    shoping_list = []
    for i in ingredients.keys():
        ingredient = Ingredient.objects.get(pk=i)
        ingredient_name = ingredient.name
        ingredient_unit = ingredient.measurement_unit
        ingredient_amount = ingredients[i]
        shoping_list.append(
            f"{ingredient_name} - {ingredient_amount} {ingredient_unit}.\n")
    filename = 'my_shopping_list.txt'
    response = HttpResponse(shoping_list, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    follow = User.objects.filter(
        following__user=request.user).annotate(
            recipes_count=Count('recipe'))
    if not User.objects.filter(
            following__user=request.user).exists():
        text = 'Тут будет список избранного.'
        return Response(text, status=status.HTTP_200_OK)
    serializer = UserFollowSerializer(follow,
                                      context={'request': request},
                                      many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites(request):
    favourites = Recipe.objects.filter(
        in_favorite__user=request.user)
    if favourites is None:
        text = 'Тут будет список избранного.'
        return Response(text, status=status.HTTP_200_OK)
    serializer = RecipeGETShortSerializer(favourites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shoping_list(request):
    shoping_list = Recipe.objects.filter(
        shopping_cart__user=request.user)
    if shoping_list is None:
        text = 'Тут будет список рецептов.'
        return Response(text, status=status.HTTP_200_OK)
    serializer = RecipeGETShortSerializer(shoping_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
