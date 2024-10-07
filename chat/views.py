from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chat
from .serializers import ChatSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        received_messages = Chat.objects.filter(recipient=request.user)
        serializer = self.get_serializer(received_messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        sent_messages = Chat.objects.filter(sender=request.user)
        serializer = self.get_serializer(sent_messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conversation(self, request, recipient_id):
        recipient = get_object_or_404(settings.AUTH_USER_MODEL, id=recipient_id)
        messages = Chat.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) | 
            (Q(sender=recipient) & Q(recipient=request.user))
        ).order_by('created_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
