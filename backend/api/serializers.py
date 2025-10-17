from django.db import transaction
from rest_framework import serializers
import base64
import six
import uuid
from django.core.files.base import ContentFile

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from recipes.models import Favorite, ShoppingCart

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = 'jpg'
            if header.startswith('data:image/'):
                file_extension = header.split('/')[1]
            complete_file_name = "%s.%s" % (file_name, file_extension)

            data = ContentFile(decoded_file, name=complete_file_name)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    author = serializers.ReadOnlyField(source='author.email')
    image = Base64ImageField(required=True)  # !!! ВОТ ТУТ !!!

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients', 'tags',
            'cooking_time', 'pub_date'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['tags'] = TagSerializer(instance.tags.all(), many=True).data
        rep['ingredients'] = RecipeIngredientSerializer(
            instance.recipeingredient_set.all(), many=True
        ).data
        rep['author'] = {
            "id": instance.author.id,
            "email": instance.author.email,
            "username": instance.author.username,
            "first_name": instance.author.first_name,
            "last_name": instance.author.last_name
        }
        return rep

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )
        instance.save()
        return instance

class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
