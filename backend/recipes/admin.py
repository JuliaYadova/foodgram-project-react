from django.contrib import admin

from .models import (Favourites, Follow, Ingredient, IngredientForRecipe,
                     Recipe, Shopping_cart, Tag)

admin.site.register(IngredientForRecipe)
admin.site.register(Favourites)
admin.site.register(Follow)
admin.site.register(Shopping_cart)


class TagAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'slug', 'color')
    search_fields = ('name',)


admin.site.register(Tag, TagAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)


class IngredientForRecipeInline(admin.TabularInline):
    model = IngredientForRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    list_display = ('name', 'author',)
    search_fields = ('username', 'email')
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    autocomplete_fields = ['tags']
    inlines = (IngredientForRecipeInline,)


admin.site.register(Recipe, RecipeAdmin)
