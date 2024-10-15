from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Comment, Hashtag, Like, Post

User = get_user_model()

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['name']

class PostSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, required=False, allow_empty=True)
    tagged_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'media', 'hashtags', 'tagged_users']

    def create(self, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        tagged_users_data = validated_data.pop('tagged_users', [])
        post = Post.objects.create(**validated_data)

        self._add_hashtags(post, hashtags_data)
        for user in tagged_users_data:
            post.tagged_users.add(user)

        return post

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        tagged_users_data = validated_data.pop('tagged_users', [])
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.media = validated_data.get('media', instance.media)
        instance.save()

        # Update hashtags and tagged users
        instance.hashtags.clear()
        self._add_hashtags(instance, hashtags_data)

        instance.tagged_users.clear()
        for user in tagged_users_data:
            instance.tagged_users.add(user)

        return instance

    def _add_hashtags(self, post, hashtags_data):
        for hashtag_data in hashtags_data:
            hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_data['name'])
            post.hashtags.add(hashtag)

    def _add_tagged_users(self, post, tagged_users_data):
        for user_data in tagged_users_data:
            user_id = user_data.get('id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    post.tagged_users.add(user)
                except User.DoesNotExist:
                    raise serializers.ValidationError({'tagged_users': f'User with ID {user_id} does not exist.'})

    # Optional: If you want to implement a method to delete posts
    def delete(self, instance):
        instance.delete()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    tagged_users = UserSerializer(many=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'media', 'tagged_users', 'created_at', 'updated_at']
        read_only_fields = ['author']  # Make author read-only, set by the viewset

    def create(self, validated_data):
        tagged_users_data = validated_data.pop('tagged_users', [])
        comment = Comment.objects.create(**validated_data)

        for user_data in tagged_users_data:
            user_id = user_data.get('id')
            if user_id:
                try:
                    user = settings.AUTH_USER_MODEL.objects.get(id=user_id)
                    comment.tagged_users.add(user)
                except User.DoesNotExist:
                    raise serializers.ValidationError({'tagged_users': f'User with ID {user_id} does not exist.'})

        return comment

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'post', 'comment']
