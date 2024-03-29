from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """Пользовательский класс наследуемый от SearchFilter.
    search_param = параметр для поиска согласно ТЗ.
    """
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """Пользовательский класс наследуемый от FilterSet.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'in_favorite', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Список избранных

        Returns:
            queryset: возвращает исходное значение или список избранных.
        """
        if value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Список покупок

        Returns:
            queryset: возвращает исходное значение или список покупок.
        """
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
