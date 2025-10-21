# from django_filters.rest_framework import (
#     FilterSet, filters)

# from recipes.models import Recipe


# class RecipeFilter(FilterSet):
#     tags = filters.AllValuesMultipleFilter(
#         field_name='tags__slug')
#     author = filters.NumberFilter(
#         field_name='author__id')
#     is_favorited = filters.BooleanFilter(
#         method='filter_is_favorited')
#     is_in_shopping_cart = filters.BooleanFilter(
#         method='filter_is_in_shopping_cart')

#     class Meta:
#         model = Recipe
#         fields = [
#             'tags',
#             'author',
#             'is_favorited',
#             'is_in_shopping_cart']

#     def filter_is_favorited(self, queryset, name, value):
#         user = getattr(self.request, 'user', None)
#         if user and user.is_authenticated and value:
#             return queryset.filter(favorites__user=user)
#         return queryset

#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         user = getattr(self.request, 'user', None)
#         if user and user.is_authenticated and value:
#             return queryset.filter(shopping_cart__user=user)
#         return queryset


# backend/api/filters.py

from django_filters import rest_framework as filters
from food.models import Recipe, Tag


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
        fields = ['author', 'tags']

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
