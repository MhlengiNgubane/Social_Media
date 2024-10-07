from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from notifications.utils import create_notification
from posts import models
from users.models import UserProfile
from users.serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied
from .models import Comment, Hashtag, Like, Post
from .serializers import CommentSerializer, LikeSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to create a post.")
        serializer.save(author=self.request.user)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        
        # Create notification for the post author
        create_notification(
            recipient=comment.post.author,
            actor=self.request.user,
            verb='commented on your post',
            target=comment
        )

class LikeViewSet(viewsets.ViewSet):
    

    def create(self, request, post_id):
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')
        post = get_object_or_404(Post, id=post_id) if post_id else None
        comment = get_object_or_404(Comment, id=comment_id) if comment_id else None

        like, created = Like.objects.get_or_create(user=request.user, post=post, comment=comment)
        if created:
            # Create notification for the post author
            create_notification(
                recipient=post.author,
                actor=request.user,
                verb='liked your post',
                target=post
            )
            return Response({'message': 'Post liked!'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already liked!'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, post_id):
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')
        like = Like.objects.filter(user=request.user, post_id=post_id, comment_id=comment_id).first()
        if like:
            like.delete()
            return Response({'message': 'Like removed!'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Like not found!'}, status=status.HTTP_404_NOT_FOUND)

class HashtagViewSet(viewsets.ViewSet):
    

    @action(detail=False, methods=['get'])
    def posts(self, request, hashtag_name):
        hashtag = get_object_or_404(Hashtag, name=hashtag_name)
        posts = hashtag.posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class FeedViewSet(viewsets.ViewSet):
    

    @action(detail=False, methods=['get'])
    def my_feed(self, request):
        user = request.user
        following = user.followers.all()  # Assuming you have followers set up
        posts = Post.objects.filter(author__in=following).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class SuggestionViewSet(viewsets.ViewSet):
    

    def list(self, request):
        user = request.user
        suggested = UserProfile.objects.exclude(user__in=user.following.all()).order_by('?')[:5]
        serializer = UserSerializer(suggested, many=True)
        return Response(serializer.data)
        
class RepostViewSet(viewsets.ViewSet):
    

    def create(self, request, post_id):
        original_post = get_object_or_404(Post, id=post_id)  # Handle post not found
        repost = Post.objects.create(
            author=request.user,
            title=f'Repost: {original_post.title}',
            content=original_post.content,
            original_post=original_post
        )
        return Response(PostSerializer(repost).data, status=status.HTTP_201_CREATED)


class TrendingPostsViewSet(viewsets.ViewSet):
    def list(self, request):
        trending_posts = Post.objects.annotate(like_count=models.Count('likes')).order_by('-like_count')[:10]
        serializer = PostSerializer(trending_posts, many=True)
        return Response(serializer.data)
