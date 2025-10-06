from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Follow, CustomUser
from .serializers import FollowSerializer, UserSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        follows = Follow.objects.filter(user=request.user)
        serializer = self.get_serializer(follows, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        author = CustomUser.objects.get(pk=pk)
        user = request.user
        if request.method == 'POST':
            if author == user:
                return Response({'error': 'Нельзя подписаться на себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            obj, created = Follow.objects.get_or_create(user=user,
                                                        author=author)
            if not created:
                return Response({'error': 'Уже подписаны.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            deleted, _ = Follow.objects.filter(
                user=user, author=author).delete()
            if not deleted:
                return Response({'error': 'Подписка не найдена.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
