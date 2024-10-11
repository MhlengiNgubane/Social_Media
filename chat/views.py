from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chat
from .serializers import ChatSerializer

User = get_user_model()

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)  # Automatically set the sender

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        received_messages = Chat.objects.filter(recipient=request.user).order_by('-created_at')
        serializer = self.get_serializer(received_messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        sent_messages = Chat.objects.filter(sender=request.user).order_by('-created_at')
        serializer = self.get_serializer(sent_messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='conversation/(?P<recipient_id>\d+)')
    def conversation(self, request, recipient_id):
        recipient = get_object_or_404(User, id=recipient_id)
        messages = Chat.objects.filter(
            Q(sender=request.user, recipient=recipient) |
            Q(sender=recipient, recipient=request.user)
        ).order_by('created_at')

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
