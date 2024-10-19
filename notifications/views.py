from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
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

@action(detail=True, methods=['post'], url_path='mark-as-read')
def mark_as_read(self, request, pk=None):
        # Get the specific notification by ID
        notification = self.get_object()

        # Mark the notification as read
        notification.is_read = True
        notification.save()

        # Return a success response
        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)