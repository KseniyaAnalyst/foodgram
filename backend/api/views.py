import os

from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientFilter
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FollowCreateSerializer,
    FollowedUserSerializer,
    FoodgramUserSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from food.models import (
    Favorite, Follow, Ingredient, Recipe,
    RecipeIngredient, ShoppingCartItem, Tag
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_queryset(self):
        queryset = Recipe.objects.all()

        user = self.request.user
        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart and user.is_authenticated:
            queryset = queryset.filter(shoppingcartitems__user=user)

        return queryset

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_short_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise NotFound(f'Рецепт с id={pk} не найден.')
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('recipe-short-link', args=[pk])
            )},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=('put',),
        url_path='me/avatar',
        permission_classes=(AllowAny,),
    )
    def set_image(self, request):
        recipe = getattr(request, 'recipe', None)
        image = request.data.get('image')

        if recipe is None:
            raise NotFound('Рецепт не найден в контексте запроса.')

        if not image:
            raise ValidationError({'image': ['Это поле обязательно.']})

        old_image_path = recipe.image.path if recipe.image else None

        recipe.image = (
            RecipeReadSerializer().fields['image'].to_internal_value(image)
        )
        recipe.save()

        if old_image_path and os.path.isfile(old_image_path):
            if old_image_path != recipe.image.path:
                try:
                    os.remove(old_image_path)
                except Exception:
                    pass

        return Response(
            {'image': recipe.image.url if recipe.image else None},
            status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shoppingcartitems__user=user)

        content = render_to_string(
            'shopping_list.txt',
            {
                'user': user,
                'date': now().date(),
                'ingredients': (
                    RecipeIngredient.objects.filter(recipe__in=recipes)
                    .values('ingredient__name', 'ingredient__measurement_unit')
                    .annotate(total_amount=models.Sum('amount'))
                    .order_by('ingredient__name')
                ),
                'recipes': recipes,
            },
        )

        response = HttpResponse(content,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response

    def handle_add_or_remove(self, *, model, recipe, request):
        if request.method not in {'POST', 'DELETE'}:
            return Response(
                {'error': f'Метод {request.method} не поддерживается'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        if request.method == 'DELETE':
            get_object_or_404(model, user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        obj, created = model.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            collection_name = model._meta.verbose_name_plural.lower()
            raise ValidationError(
                f'Рецепт с id={recipe.id} уже добавлен в {collection_name}.'
            )

        return Response(
            ShortRecipeSerializer(recipe, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        return self.handle_add_or_remove(
            model=ShoppingCartItem, request=request, recipe=recipe
        )

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        return self.handle_add_or_remove(
            model=Favorite, recipe=recipe, request=request
        )


class UserWithSubscriptionViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(detail=False, methods=('put', 'delete'), url_path='me/avatar',
            permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            avatar = request.data.get('avatar')
            if not avatar:
                raise ValidationError({'avatar': ['Это поле обязательно.']})

            user.avatar = (
                FoodgramUserSerializer(context={'request': request})
                .fields['avatar']
                .to_internal_value(avatar)
            )
            user.save()

            return Response(
                {'avatar': user.avatar.url if user.avatar else None},
                status=status.HTTP_200_OK
            )

        old_path = user.avatar.path if (
            user.avatar and getattr(user.avatar, 'path', None)
        ) else None
        if old_path and os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        pk = kwargs['id']
        user = request.user

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, follower=request.user, author_id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = get_object_or_404(User, pk=pk)

        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя')

        serializer = FollowCreateSerializer(
            data={'follower': user.id, 'author': author.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        out = FollowedUserSerializer(author, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            pk__in=Follow.objects.filter(
                follower=request.user
            ).values_list('author__id', flat=True)
        )
        paginator = RecipePagination()
        return paginator.get_paginated_response(
            FollowedUserSerializer(
                paginator.paginate_queryset(authors, request),
                many=True,
                context={'request': request},
            ).data
        )
