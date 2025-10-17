from django.db import transaction
from rest_framework import serializers

from recipes.models import (
    Tag, Ingredient, Recipe,
    RecipeIngredient, Favorite, ShoppingCart
)


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
            raise serializers.ValidationError("Количество ингредиента должно быть > 0.")
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)
    ingredients_detail = RecipeIngredientReadSerializer(
        source='recipeingredient_set', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'cooking_time',
            'tags', 'ingredients', 'ingredients_detail',
            'is_favorited', 'is_in_shopping_cart', 'pub_date'
        )
        read_only_fields = ('id', 'author', 'pub_date')

    def get_is_favorited(self, obj):
        user = self._user()
        if not user:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self._user()
        if not user:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def _user(self):
        req = self.context.get('request')
        if not req or not hasattr(req, 'user') or req.user.is_anonymous:
            return None
        return req.user

    def validate(self, attrs):
        tags = attrs.get('tags', [])
        ingredients = attrs.get('ingredients', [])
        cooking_time = attrs.get('cooking_time')

        tag_ids = [t.id if isinstance(t, Tag) else int(t) for t in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError({"tags": "Теги не должны повторяться."})

        if not ingredients:
            raise serializers.ValidationError({"ingredients": "Нужен хотя бы один ингредиент."})

        seen = set()
        for item in ingredients:
            iid = int(item['id'])
            if iid in seen:
                raise serializers.ValidationError({"ingredients": "Ингредиенты не должны повторяться."})
            seen.add(iid)
            if int(item.get('amount', 0)) < 1:
                raise serializers.ValidationError({"ingredients": "Количество должно быть > 0."})

        if cooking_time is None or int(cooking_time) < 1:
            raise serializers.ValidationError({"cooking_time": "Время готовки должно быть > 0."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)

        if tags:
            recipe.tags.set(tags)

        self._set_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            self._set_ingredients(instance, ingredients_data)

        instance.save()
        return instance

    def _set_ingredients(self, recipe, ingredients_data):
        bulk = []
        requested_ids = [int(i['id']) for i in ingredients_data]
        id_to_obj = {ing.id: ing for ing in Ingredient.objects.filter(id__in=requested_ids)}

        missing = [iid for iid in requested_ids if iid not in id_to_obj]
        if missing:
            raise serializers.ValidationError({"ingredients": f"Нет ингредиентов с id: {missing}"})

        for item in ingredients_data:
            ing = id_to_obj[int(item['id'])]
            amount = int(item['amount'])
            if amount < 1:
                raise serializers.ValidationError({"ingredients": "Количество должно быть > 0."})
            bulk.append(RecipeIngredient(recipe=recipe, ingredient=ing, amount=amount))
        RecipeIngredient.objects.bulk_create(bulk)
