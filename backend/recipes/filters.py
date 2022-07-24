from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'in_favorite', 'in_shopping_cart')

    def filter_in_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_list__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
