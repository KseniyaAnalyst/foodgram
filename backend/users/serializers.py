from rest_framework import serializers

from .models import CustomUser, Follow
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class FollowSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'author', 'recipes', 'recipes_count', 'created')

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return [
            {
                "id": recipe.id,
                "name": recipe.name,
                "image": recipe.image.url if recipe.image else "",
                "cooking_time": recipe.cooking_time,
            }
            for recipe in recipes
        ]

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
