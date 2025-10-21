# from django.db import transaction
# from django.core.files.base import ContentFile
# from django.core.files.uploadedfile import SimpleUploadedFile
# from rest_framework import serializers
# import base64
# import binascii

# from recipes.models import (
#     Tag, Ingredient, Recipe,
#     RecipeIngredient, Favorite, ShoppingCart
# )


# def decode_data_url(data: str) -> SimpleUploadedFile:
#     if not isinstance(data, str):
#         raise serializers.ValidationError('Некорректные данные изображения')

#     # Удаляем пробелы/переносы, которые иногда вставляет фронт
#     data = data.strip()

#     mime = 'image/jpeg'
#     ext = 'jpg'
#     b64data = data

#     if data.startswith('data:image'):
#         if ';base64,' not in data:
#             raise serializers.ValidationError(
# 'Некорректные данные изображения: нет ;base64,')
#         header, b64data = data.split(';base64,', 1)
#         try:
#             mime = header.split(':', 1)[1]  # 'image/png'
#         except Exception:
#             mime = 'image/jpeg'
#         try:
#             ext = mime.split('/')[-1].lower()
#             if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
#                 ext = 'jpg'
#         except Exception:
#             ext = 'jpg'
#     else:
#         # «Голая» base64 без префикса — допустим, как jpeg
#         mime = 'image/jpeg'
#         ext = 'jpg'

#     try:
#         # strict decode
#         decoded = base64.b64decode(b64data, validate=True)
#     except (binascii.Error, ValueError):
#         raise serializers.ValidationError(
# 'Некорректные данные изображения: не удалось декодировать base64')

#     # создаём «настоящий» загруженный файл с content_type
#     return SimpleUploadedFile(
#         name=f'upload.{ext}',
#         content=decoded,
#         content_type=mime
#     )


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ('id', 'name', 'color', 'slug')


# class IngredientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name', 'measurement_unit')


# class RecipeIngredientReadSerializer(serializers.ModelSerializer):
#     id = serializers.ReadOnlyField(source='ingredient.id')
#     name = serializers.ReadOnlyField(source='ingredient.name')
#     measurement_unit = serializers.ReadOnlyField(
#         source='ingredient.measurement_unit'
#     )

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'measurement_unit', 'amount')


# class RecipeIngredientWriteSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     amount = serializers.IntegerField()

#     def validate_amount(self, value):
#         if value < 1:
#             raise serializers.ValidationError(
#                 'Количество ингредиента должно быть > 0.'
#             )
#         return value


# class ShortRecipeSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField()

#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')
#         read_only_fields = fields

#     def get_image(self, obj):
#         request = self.context.get('request')
#         if not obj.image:
#             return ''
#         url = obj.image.url
#         return request.build_absolute_uri(url) if request else url


# class RecipeSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username'
#     )
#     image = serializers.CharField(write_only=True)
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(), many=True
#     )
#     ingredients = RecipeIngredientWriteSerializer(
#         many=True, write_only=True
#     )
#     ingredients_detail = RecipeIngredientReadSerializer(
#         source='recipeingredient_set', many=True, read_only=True
#     )
#     is_favorited = serializers.SerializerMethodField(read_only=True)
#     is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'author', 'name', 'image', 'text', 'cooking_time',
#             'tags', 'ingredients', 'ingredients_detail',
#             'is_favorited', 'is_in_shopping_cart', 'pub_date'
#         )
#         read_only_fields = ('id', 'author', 'pub_date')

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         # заменяем поле image на URL
#         request = self.context.get('request')
#         if instance.image:
#             url = instance.image.url
#             data['image'] = request.build_absolute_uri(url)
# if request else url
#         else:
#             data['image'] = ''
#         return data

#     def get_is_favorited(self, obj):
#         user = self._user()
#         if not user:
#             return False
#         return Favorite.objects.filter(user=user, recipe=obj).exists()

#     def get_is_in_shopping_cart(self, obj):
#         user = self._user()
#         if not user:
#             return False
#         return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

#     def _user(self):
#         request_obj = self.context.get('request')
#         if (
#             not request_obj
#             or not hasattr(request_obj, 'user')
#             or request_obj.user.is_anonymous
#         ):
#             return None
#         return request_obj.user

#     def validate(self, attrs):
#         tags = attrs.get('tags', [])
#         ingredients = attrs.get('ingredients', [])
#         cooking_time = attrs.get('cooking_time')

#         tag_ids = [
#             tag.id if isinstance(tag, Tag) else int(tag)
#             for tag in tags
#         ]
#         if len(tag_ids) != len(set(tag_ids)):
#             raise serializers.ValidationError(
#                 {'tags': 'Теги не должны повторяться.'}
#             )

#         if not ingredients:
#             raise serializers.ValidationError(
#                 {'ingredients': 'Нужен хотя бы один ингредиент.'}
#             )

#         seen = set()
#         for ingredient_item in ingredients:
#             ingredient_id = int(ingredient_item['id'])
#             if ingredient_id in seen:
#                 raise serializers.ValidationError(
#                     {'ingredients': 'Ингредиенты не должны повторяться.'}
#                 )
#             seen.add(ingredient_id)

#         if cooking_time is None or int(cooking_time) < 1:
#             raise serializers.ValidationError(
#                 {'cooking_time': 'Время готовки должно быть > 0.'}
#             )

#         return attrs

#     def _set_ingredients(self, recipe, ingredients_data):
#         bulk = []
#         requested_ids = [int(item['id']) for item in ingredients_data]
#         id_to_ingredient = {
#             ing.id: ing
#             for ing in Ingredient.objects.filter(id__in=requested_ids)
#         }

#         missing = [
#             ingredient_id
#             for ingredient_id in requested_ids
#             if ingredient_id not in id_to_ingredient
#         ]
#         if missing:
#             raise serializers.ValidationError(
#                 {'ingredients': f'Нет ингредиентов с id: {missing}'}
#             )

#         for item in ingredients_data:
#             ingredient = id_to_ingredient[int(item['id'])]
#             amount = int(item['amount'])
#             bulk.append(
#                 RecipeIngredient(
#                     recipe=recipe, ingredient=ingredient, amount=amount
#                 )
#             )
#         RecipeIngredient.objects.bulk_create(bulk)

#     @transaction.atomic
#     def create(self, validated_data):
#         # Достаём сырой base64 и превращаем в файл
#         image_raw = validated_data.pop('image', None)
#         ingredients_data = validated_data.pop('ingredients', [])
#         tags = validated_data.pop('tags', [])
#         request = self.context.get('request')

#         recipe = Recipe.objects.create(
#             author=request.user, **validated_data
#         )

#         if image_raw:
#             upload = decode_data_url(image_raw)
#             # сохраняем напрямую, минуя валидацию DRF-поля
#             recipe.image.save(
# upload.name, ContentFile(upload.read()), save=False)

#         if tags:
#             recipe.tags.set(tags)

#         self._set_ingredients(recipe, ingredients_data)
#         recipe.save()
#         return recipe

#     @transaction.atomic
#     def update(self, instance, validated_data):
#         image_raw = validated_data.pop('image', None)
#         ingredients_data = validated_data.pop('ingredients', None)
#         tags = validated_data.pop('tags', None)

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         if image_raw is not None:
#             upload = decode_data_url(image_raw)
#             instance.image.save(
# upload.name, ContentFile(upload.read()), save=False)

#         if tags is not None:
#             instance.tags.set(tags)

#         if ingredients_data is not None:
#             instance.recipeingredient_set.all().delete()
#             self._set_ingredients(instance, ingredients_data)

#         instance.save()
#         return instance


# class FavoriteCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Favorite
#         fields = ('user', 'recipe')


# class ShoppingCartCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShoppingCart
#         fields = ('user', 'recipe')

from collections import Counter

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from food.constants import INGREDIENT_MIN_AMOUNT, RECIPE_MIN_COOKING_TIME
from food.models import (Favorite, Follow, Ingredient, Recipe,
                         RecipeIngredient, ShoppingCartItem, Tag)
from library.base64ImageField import Base64ImageField

User = get_user_model()


class FoodgramUserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (*DjoserUserSerializer.Meta.fields, 'avatar', 'is_subscribed')
        read_only_fields = fields

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and Follow.objects.filter(author=author,
                                      follower=request.user).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        min_value=INGREDIENT_MIN_AMOUNT,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientReadSerializer(
        source='ingredients_in_recipe',
        many=True
    )
    author = FoodgramUserSerializer()
    tags = TagSerializer(many=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')
        read_only_fields = fields

    def check_user_status(self, recipe, model_class):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and model_class.objects.filter(user=request.user,
                                           recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        return self.check_user_status(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_user_status(recipe, ShoppingCartItem)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        required=True,
        label='Ингредиенты',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        label='Теги',
    )
    cooking_time = serializers.IntegerField(
        min_value=RECIPE_MIN_COOKING_TIME,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['ingredient'].id,
                amount=item['amount']
            )
            for item in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        validated_data['author'] = self.context['request'].user
        recipe = super().create(validated_data)

        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        instance.tags.set(tags_data)
        instance.ingredients_in_recipe.all().delete()
        self.create_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент.')
        duplicate_ids = {
            id_ for id_, count in
            Counter(item['ingredient'].id for item in ingredients).items()
            if count > 1
        }
        if not duplicate_ids:
            return ingredients

        names = Ingredient.objects.filter(
            id__in=duplicate_ids).values_list('name', flat=True)

        raise serializers.ValidationError(
            f'Ингредиенты не должны повторяться: {names}.')

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Нужно выбрать хотя бы один тег.')

        duplicate_ids = {
            id_ for id_, count in
            Counter(getattr(tag, 'id') for tag in tags).items()
            if count > 1
        }
        if not duplicate_ids:
            return tags

        names = (Tag.objects.filter(id__in=duplicate_ids)
                 .values_list('name', flat=True))
        raise serializers.ValidationError(
            f'Теги не должны повторяться: {names}.'
        )

    def validate(self, data):
        request_method = self.context['request'].method

        if request_method in ('POST', 'PATCH'):
            if 'ingredients' not in data:
                raise serializers.ValidationError(
                    {'ingredients': 'Это поле обязательно.'})
            if 'tags' not in data:
                raise serializers.ValidationError(
                    {'tags': 'Это поле обязательно.'})

        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, followed_user):
        user = self.context['request'].user
        return user.is_authenticated and Follow.objects.filter(
            follower=user, author=followed_user
        ).exists()

    class Meta:
        model = User
        fields = (*DjoserUserSerializer.Meta.fields,
                  'avatar', 'is_subscribed')
        read_only_fields = fields


class FollowedUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (*UserSerializer.Meta.fields,
                  'recipes', 'recipes_count')
        read_only_fields = fields

    def get_recipes(self, obj):
        return ShortRecipeSerializer(
            obj.recipes.all()[
                :int(self.context['request'].
                     GET.get('recipes_limit', 10 ** 10))
            ],
            many=True,
            context=self.context
        ).data
