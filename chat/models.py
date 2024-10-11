from django.conf import settings
from django.db import models


class Chat(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    media = models.FileField(upload_to='media/chats/', blank=True, null=True)  # For images, videos, or files
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Chats"

    def __str__(self):
        return f'Message from {self.sender} to {self.recipient} at {self.created_at}'
    