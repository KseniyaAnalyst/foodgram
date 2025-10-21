# from django.urls import path, include
# from rest_framework.routers import DefaultRouter

# from .views import (
#     TagViewSet, IngredientViewSet,
#     RecipeViewSet)
# from .views_users import FollowViewSet

# router = DefaultRouter()
# router.register(r'tags', TagViewSet, basename='tag')
# router.register(r'ingredients', IngredientViewSet, basename='ingredient')
# router.register(r'recipes', RecipeViewSet, basename='recipe')
# router.register(
#     r'users/subscriptions', FollowViewSet, basename='subscriptions')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

# api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserWithSubscriptionViewSet)

api = DefaultRouter()

api.register(r'ingredients',
             IngredientViewSet, basename='ingredients')
api.register(r'recipes', RecipeViewSet, basename='recipes')
api.register(r'tags', TagViewSet, basename='tags')
api.register(r'users', UserWithSubscriptionViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(api.urls)),
]
