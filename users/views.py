from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from notifications.utils import create_notification
from posts.models import Post
from posts.serializers import PostSerializer

from .serializers import (LoginSerializer, RegisterSerializer, User,
                          UserSerializer)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow == request.user:
        return Response({'message': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.followers.add(user_to_follow)
    
    # Create a notification for the follow action
    create_notification(
        recipient=user_to_follow,
        actor=request.user,
        verb='started following you',
        target=user_to_follow
    )

    return Response({'message': f'You are now following {user_to_follow.username}'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    if user_to_unfollow == request.user:
        return Response({'message': 'You cannot unfollow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.followers.remove(user_to_unfollow)
    return Response({'message': f'You have unfollowed {user_to_unfollow.username}'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow == request.user:
        return Response({'message': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.followers.add(user_to_follow)
    
    # Create a notification for the follow action
    create_notification(
        recipient=user_to_follow,
        actor=request.user,
        verb='started following you',
        target=user_to_follow
    )

    return Response({'message': f'You are now following {user_to_follow.username}'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    if user_to_unfollow == request.user:
        return Response({'message': 'You cannot unfollow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.followers.remove(user_to_unfollow)
    return Response({'message': f'You have unfollowed {user_to_unfollow.username}'}, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, user_id):
        user = get_object_or_404(settings.AUTH_USER_MODEL, id=user_id)
        posts = Post.objects.filter(author=user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
