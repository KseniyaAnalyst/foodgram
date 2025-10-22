from django_filters import rest_framework as filters
from django_filters.filterset import FilterSet
from django_filters.filters import CharFilter
from food.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        label='tags',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, recipes, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return recipes.filter(favorites__user=user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return recipes.filter(shoppingcartitems__user=user)
        return recipes
