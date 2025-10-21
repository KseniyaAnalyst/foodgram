# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

# from recipes.models import Recipe
# from users.models import Follow


# User = get_user_model()


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name')


# class FollowSerializer(serializers.ModelSerializer):
#     author = UserSerializer(read_only=True)
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = Follow
#         fields = ('id', 'author', 'recipes', 'recipes_count', 'created')
#         read_only_fields = ('id', 'created')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'author'),
#                 message='Вы уже подписаны на этого автора.',
#             )
#         ]

#     def validate_author(self, value):
#         user = self.context['request'].user
#         if value == user:
#             raise serializers.ValidationError(
#                 'Нельзя подписаться на самого себя.')
#         return value

#     def get_recipes(self, obj):
#         recipes_qs = obj.author.recipes.all()
#         return [
#             {
#                 'id': recipe.id,
#                 'name': recipe.name,
#                 'image': recipe.image.url if recipe.image else '',
#                 'cooking_time': recipe.cooking_time,
#             }
#             for recipe in recipes_qs
#         ]

#     def get_recipes_count(self, obj):
#         return obj.author.recipes.count()
