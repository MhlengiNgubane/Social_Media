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
    queryset = Post.objects.all()  # Query all posts from the database
    serializer_class = PostSerializer  # Use the PostSerializer to handle serialization/deserialization
    permission_classes = [IsAuthenticated]  # Require users to be authenticated for all actions

    def perform_create(self, serializer):
        # Automatically set the author of the post to the currently logged-in user
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        # Handle the creation of a new post
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the request data
        self.perform_create(serializer)  # Save the post
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the created post with a 201 status

    def update(self, request, *args, **kwargs):
        # Handle updating an existing post
        post = self.get_object()  # Get the post to be updated
        serializer = self.get_serializer(post, data=request.data, partial=True)  # Partial updates allowed
        serializer.is_valid(raise_exception=True)  # Validate the update data
        self.perform_update(serializer)  # Update the post
        return Response(serializer.data)  # Return the updated post

    def destroy(self, request, *args, **kwargs):
        # Handle deleting a post
        post = self.get_object()  # Get the post to be deleted
        post.delete()  # Delete the post
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return a 204 No Content response

    def list(self, request, *args, **kwargs):
        # List all posts
        queryset = self.get_queryset()  # Get all posts
        serializer = self.get_serializer(queryset, many=True)  # Serialize the list of posts
        return Response(serializer.data)  # Return the serialized data

    def retrieve(self, request, *args, **kwargs):
        # Retrieve a single post by ID
        post = self.get_object()  # Get the specific post
        serializer = self.get_serializer(post)  # Serialize the post
        return Response(serializer.data)  # Return the serialized post


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()  # Query all comments from the database
    serializer_class = CommentSerializer  # Use CommentSerializer for comments
    permission_classes = [IsAuthenticated]  # Require authentication for all comment actions

    def perform_create(self, serializer):
        # Create a new comment and associate it with the logged-in user
        comment = serializer.save(author=self.request.user)

        # Notify the post author that someone commented on their post
        create_notification(
            recipient=comment.post.author,  # Recipient is the post author
            actor=self.request.user,  # Actor is the logged-in user who made the comment
            verb='commented on your post',  # Notification message
            target=comment  # The comment itself is the target of the notification
        )

        # Notify any users that were tagged in the comment
        for user in comment.tagged_users.all():
            create_notification(
                recipient=user,  # Recipient is the tagged user
                actor=self.request.user,  # Actor is the logged-in user
                verb='tagged you in a comment',  # Notification message
                target=comment  # The comment is the notification target
            )

    def perform_update(self, serializer):
        # Update the comment (also handles tagging changes)
        comment = serializer.save()

        # Notify any newly tagged users
        for user in comment.tagged_users.all():
            create_notification(
                recipient=user,  # Notify the newly tagged user
                actor=self.request.user,  # Actor is the logged-in user
                verb='tagged you in a comment',  # Notification message
                target=comment  # The updated comment is the target
            )

    def perform_destroy(self, instance):
        # Handle deleting a comment
        instance.delete()  # Simply delete the comment

    @action(detail=True, methods=['get'], url_path='comments')
    def get_comments(self, request, pk=None):
        # Retrieve all comments for a specific post
        post = get_object_or_404(Post, pk=pk)  # Find the post by its primary key (ID)
        comments = post.comments.all()  # Get all comments associated with the post
        serializer = self.get_serializer(comments, many=True)  # Serialize the list of comments
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the serialized comments


class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Only authenticated users can like/unlike

    def get_post_and_comment(self, request):
        # Utility function to get a post or a comment from the request data
        post_id = request.data.get('post_id')  # Get post ID from the request data
        comment_id = request.data.get('comment_id')  # Get comment ID from the request data
        post = get_object_or_404(Post, id=post_id) if post_id else None  # Get post if post_id is provided
        comment = get_object_or_404(Comment, id=comment_id) if comment_id else None  # Get comment if comment_id is provided
        return post, comment  # Return both post and comment objects

    def create(self, request):
        # Handle liking a post or a comment
        post, comment = self.get_post_and_comment(request)  # Get the post or comment being liked

        # Try to create a new like, or check if it already exists
        like, created = Like.objects.get_or_create(user=request.user, post=post, comment=comment)
        if created:
            # If the like is created, notify the post author (if it's a post)
            if post:
                create_notification(
                    recipient=post.author,  # Notify the post author
                    actor=request.user,  # Actor is the logged-in user
                    verb='liked your post',  # Notification message
                    target=post  # The post is the notification target
                )
            return Response({'message': 'liked!', 'id': like.id}, status=status.HTTP_201_CREATED)  # Return success with like ID
        return Response({'message': 'Already liked!'}, status=status.HTTP_400_BAD_REQUEST)  # If already liked, return an error

    def destroy(self, request, pk=None):
        # Handle unliking (removing a like)
        try:
            like = Like.objects.get(id=pk, user=request.user)  # Find the like by its ID and user
            like.delete()  # Delete the like
            return Response({'message': 'Like removed!'}, status=status.HTTP_204_NO_CONTENT)  # Return success message
        except Like.DoesNotExist:
            return Response({'message': 'Like not found!'}, status=status.HTTP_404_NOT_FOUND)  # Return error if like doesn't exist


class HashtagViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Require authentication

    @action(detail=False, methods=['get'])
    def posts(self, request, hashtag_name):
        # Retrieve posts associated with a specific hashtag
        hashtag = get_object_or_404(Hashtag, name=hashtag_name)  # Find the hashtag by its name
        posts = hashtag.posts.all()  # Get all posts with this hashtag
        serializer = PostSerializer(posts, many=True)  # Serialize the list of posts
        return Response(serializer.data)  # Return the serialized posts


class FeedViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Require authentication

    @action(detail=False, methods=['get'])
    def my_feed(self, request):
        # Retrieve the authenticated user's feed (posts from followed users)
        user = request.user  # Get the logged-in user
        following = user.followers.all()  # Get the list of users the current user follows
        posts = Post.objects.filter(author__in=following).order_by('-created_at')  # Get posts from followed users, ordered by most recent
        serializer = PostSerializer(posts, many=True)  # Serialize the posts
        return Response(serializer.data)  # Return the serialized feed


class SuggestionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Require authentication

    def list(self, request):
        # Provide a list of suggested users to follow
        user = request.user  # Get the logged-in user
        # Suggest users that the current user is not already following, and return a random 5
        suggested = UserProfile.objects.exclude(user__in=user.following.all()).order_by('?')[:5]
        serializer = UserSerializer(suggested, many=True)  # Serialize the suggested users
        return Response(serializer.data)  # Return the serialized suggestions


class RepostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Require authentication

    def create(self, request, post_id):
        # Handle reposting a post
        original_post = get_object_or_404(Post, id=post_id)  # Get the original post being reposted
        repost = Post.objects.create(
            author=request.user,  # Set the current user as the author of the repost
            title=f'Repost: {original_post.title}',  # Add 'Repost:' to the original post's title
            content=original_post.content,  # Copy the content of the original post
            original_post=original_post  # Set the original post as the reference for this repost
        )
        return Response(PostSerializer(repost).data, status=status.HTTP_201_CREATED)  # Return the newly created repost


class TrendingPostsViewSet(viewsets.ViewSet):
    def list(self, request):
        # Retrieve a list of trending posts based on the number of likes
        trending_posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:10]  # Annotate posts with like counts and order by most liked
        serializer = PostSerializer(trending_posts, many=True)  # Serialize the trending posts
        return Response(serializer.data)  # Return the serialized trending posts
