from django.db import models
from django.http import HttpResponse

from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated, AllowAny)
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import RecipeFilter

from recipes.models import (
    Tag, Ingredient, Recipe,
    Favorite, ShoppingCart,
    RecipeIngredient,
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    ShortRecipeSerializer
, FavoriteCreateSerializer, ShoppingCartCreateSerializer)
from .permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects
        .select_related('author')
        .prefetch_related(
            'tags', 'recipeingredient_set__ingredient')
        .order_by('-pub_date')
    )
    serializer_class = RecipeSerializer

    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=('post',),
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        create_serializer = FavoriteCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id})
        create_serializer.is_valid(raise_exception=True)
        create_serializer.save()
        response_serializer = ShortRecipeSerializer(recipe)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=('post',),
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        create_serializer = ShoppingCartCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id})
        create_serializer.is_valid(raise_exception=True)
        create_serializer.save()
        response_serializer = ShortRecipeSerializer(recipe)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount_sum=models.Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = [
            f'{ing["ingredient__name"]} '
            f'({ing["ingredient__measurement_unit"]}) — '
            f'{ing["amount_sum"]}'
            for ing in ingredients
        ]
        content = '\n'.join(lines) if lines else 'Список пуст.'
        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"' )
        return response
