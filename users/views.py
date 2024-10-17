from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.utils import create_notification
from posts.models import Post
from posts.serializers import PostSerializer

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'user': UserSerializer(user).data, 'token': token.key}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # Delete the user's token
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class FollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        if user_to_follow == request.user:
            return Response({'message': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.followers.add(user_to_follow)
        
        create_notification(
        recipient=user_to_follow,
        actor=request.user,
        verb='started following you',
        target=user_to_follow
    )
        return Response({'message': f'You are now following {user_to_follow.username}'}, status=status.HTTP_200_OK)

class UnfollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        user_to_unfollow = get_object_or_404(User, id=user_id)
        if user_to_unfollow == request.user:
            return Response({'message': 'You cannot unfollow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.followers.remove(user_to_unfollow)
        return Response({'message': f'You have unfollowed {user_to_unfollow.username}'}, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        posts = Post.objects.filter(author=user).order_by('-created_at')  # Ensure Post model is imported
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
