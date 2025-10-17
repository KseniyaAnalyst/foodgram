from rest_framework import serializers
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from django.db import transaction

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)
    author = serializers.ReadOnlyField(source='author.email')
    image = serializers.ImageField(required=True)
    ingredients_read = RecipeIngredientReadSerializer(source='recipeingredient_set', many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'ingredients_read',
            'tags', 'cooking_time', 'pub_date'
        )
        read_only_fields = ('author', 'ingredients_read')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['ingredients'] = rep.pop('ingredients_read')
        rep['tags'] = TagSerializer(instance.tags.all(), many=True).data
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
        self.create_ingredients(recipe, ingredients_data)
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
            self.create_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def create_ingredients(self, recipe, ingredients_data):
        objs = []
        for ing in ingredients_data:
            ingredient = Ingredient.objects.get(pk=ing['id'])
            objs.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=ing['amount']
            ))
        RecipeIngredient.objects.bulk_create(objs)
