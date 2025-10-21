# from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model

# from rest_framework import viewsets, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework.exceptions import ValidationError, NotFound

# from users.models import Follow
# from .serializers_users import FollowSerializer, UserSerializer

# User = get_user_model()


# class FollowViewSet(viewsets.ModelViewSet):
#     serializer_class = FollowSerializer
#     permission_classes = (IsAuthenticated,)

#     def get_queryset(self):
#         return self.request.user.follower.all()

#     @action(detail=False, methods=('get',))
#     def subscriptions(self, request):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

#     @action(detail=True, methods=('post', 'delete'))
#     def subscribe(self, request, pk=None):
#         user = request.user
#         author = get_object_or_404(User, pk=pk)

#         if request.method == 'POST':
#             data = {'user': user.id, 'author': author.id}
#             serializer = self.get_serializer(
#                 data=data, context={'request': request})
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             user_serializer = UserSerializer(author)
#             return Response(
#                 user_serializer.data, status=status.HTTP_201_CREATED)

#         deleted, _ = user.follower.filter(author=author).delete()
#         if not deleted:
#             raise NotFound('Подписка не найдена.')
#         return Response(status=status.HTTP_204_NO_CONTENT)
