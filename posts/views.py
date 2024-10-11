from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.utils import create_notification
from posts import models
from posts.models import Hashtag, Like, Post
from users.models import UserProfile
from users.serializers import UserSerializer

from .models import Comment
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for all actions

    def perform_create(self, serializer):
        # Automatically set the author to the currently authenticated user
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        post = self.get_object()  # Get the post instance
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()  # Get the post instance
        post.delete()  # Delete the post
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # Get all posts
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()  # Get a specific post instance
        serializer = self.get_serializer(post)
        return Response(serializer.data)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the author to the currently authenticated user
        comment = serializer.save(author=self.request.user)
        create_notification(
            recipient=comment.post.author,
            actor=self.request.user,
            verb='commented on your post',
            target=comment
        )
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_post_and_comment(self, request):
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')
        post = get_object_or_404(Post, id=post_id) if post_id else None
        comment = get_object_or_404(Comment, id=comment_id) if comment_id else None
        return post, comment

    def create(self, request):
        post, comment = self.get_post_and_comment(request)

        like, created = Like.objects.get_or_create(user=request.user, post=post, comment=comment)
        if created:
            if post:
                create_notification(
                    recipient=post.author,
                    actor=request.user,
                    verb='liked your post',
                    target=post
                )
            return Response({'message': 'Post liked!', 'id': like.id}, status=status.HTTP_201_CREATED)  # Return the like ID
        return Response({'message': 'Already liked!'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # Retrieve the like by its primary key (pk)
        try:
            like = Like.objects.get(id=pk, user=request.user)
            like.delete()
            return Response({'message': 'Like removed!'}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({'message': 'Like not found!'}, status=status.HTTP_404_NOT_FOUND)

class HashtagViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def posts(self, request, hashtag_name):
        hashtag = get_object_or_404(Hashtag, name=hashtag_name)
        posts = hashtag.posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class FeedViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_feed(self, request):
        user = request.user
        following = user.followers.all()  # Assuming followers relationship exists
        posts = Post.objects.filter(author__in=following).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class SuggestionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        suggested = UserProfile.objects.exclude(user__in=user.following.all()).order_by('?')[:5]
        serializer = UserSerializer(suggested, many=True)
        return Response(serializer.data)

class RepostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, post_id):
        original_post = get_object_or_404(Post, id=post_id)
        repost = Post.objects.create(
            author=request.user,
            title=f'Repost: {original_post.title}',
            content=original_post.content,
            original_post=original_post
        )
        return Response(PostSerializer(repost).data, status=status.HTTP_201_CREATED)

class TrendingPostsViewSet(viewsets.ViewSet):
    def list(self, request):
        trending_posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:10]
        serializer = PostSerializer(trending_posts, many=True)
        return Response(serializer.data)
