from django.contrib import admin

from .models import (Favourite, Follow, Ingredient, IngredientForRecipe,
                     Recipe, ShoppingCart, Tag)

admin.site.register(IngredientForRecipe)
admin.site.register(Favourite)
admin.site.register(Follow)
admin.site.register(ShoppingCart)


class TagAdmin(admin.ModelAdmin):
    """Уточнение параметров отражения Тэгов и строка поиска.
    """
    list_display = ('colored_name', 'slug', 'color')
    search_fields = ('name',)


admin.site.register(Tag, TagAdmin)


class IngredientAdmin(admin.ModelAdmin):
    """Уточнение параметров отражения Ингридиентов
    , строка поиска, поле фильтра.
    """
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)


class IngredientForRecipeInline(admin.TabularInline):
    """Класс для подключения связанной таблицы
    Ингридиенты для рецептов к зоне Админа.
    """
    model = IngredientForRecipe
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Настройка модели отражения рецепта.
    Настроена: иерархия отражения, поля отражения,
    поля поиска, поля фильтра, настройка поля выбора Тэга,
    связанная таблица подключена через вспомогательный класс.
    """
    date_hierarchy = 'pub_date'
    list_display = ('name', 'author', 'count_in_favorite')
    search_fields = ('username', 'email')
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    autocomplete_fields = ['tags']
    inlines = (IngredientForRecipeInline,)

    def count_in_favorite(self, obj):
        """Пользовательское поле в Админ зоне Рецепта.
        Количество добавлений рецепта в избранное.

        Args:
            obj (Recipe): объект рецепта.

        Returns:
            int: посчитанное количество у каждого объекта булевого поля
            в избранном.
        """
        return obj.in_favorite.count()


admin.site.register(Recipe, RecipeAdmin)
