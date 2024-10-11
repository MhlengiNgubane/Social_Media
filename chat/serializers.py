from rest_framework import serializers

from .models import Chat


class ChatSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')  # Makes sender read-only

    class Meta:
        model = Chat
        fields = ['id', 'sender', 'recipient', 'content', 'media', 'created_at']
        