from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return notifications for the authenticated user
        return self.queryset.filter(recipient=self.request.user).order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Optionally, you can highlight unread notifications
        unread_notifications = queryset.filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_notifications.count()
        })
