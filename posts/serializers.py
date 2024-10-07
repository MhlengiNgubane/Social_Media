from django.conf import settings
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Comment, Hashtag, Like, Post


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['name']

class PostSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, required=False, allow_empty=True)  # Optional field
    tagged_users = UserSerializer(many=True, required=False)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'media', 'hashtags', 'tagged_users']  # Include other fields as needed

    def create(self, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        tagged_users_data = validated_data.pop('tagged_users', [])
        post = Post.objects.create(**validated_data)

        for hashtag_data in hashtags_data:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_data['name'])
            post.hashtags.add(hashtag)

        for user_data in tagged_users_data:
            user = settings.AUTH_USER_MODEL.objects.get(id=user_data['id'])
            post.tagged_users.add(user)
            
        return post

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.media = validated_data.get('media', instance.media)
        instance.save()

        # Update hashtags
        instance.hashtags.clear()  # Clear existing hashtags
        for hashtag_data in hashtags_data:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_data['name'])
            instance.hashtags.add(hashtag)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    tagged_users = UserSerializer(many=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'media', 'tagged_users', 'created_at', 'updated_at']

    def create(self, validated_data):
        tagged_users_data = validated_data.pop('tagged_users', [])
        comment = Comment.objects.create(**validated_data)

        for user_data in tagged_users_data:
            user = settings.AUTH_USER_MODEL.objects.get(id=user_data['id'])
            comment.tagged_users.add(user)

        return comment
    

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'post', 'comment']
