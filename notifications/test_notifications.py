import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification
from notifications.utils import create_notification
from posts.models import Post

User = get_user_model()

@pytest.mark.django_db
class NotificationTest(APITestCase):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')
        self.client.login(username='user1', password='pass')

    def test_create_notification(self):
        post = Post.objects.create(author=self.user2, title='Test Post', content='Content here')
        create_notification(recipient=self.user1, actor=self.user2, verb='liked', target=post)

        notification = Notification.objects.first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.actor, self.user2)
        self.assertEqual(notification.verb, 'liked')
        self.assertEqual(notification.target, post)

    def test_notification_view(self):
        post = Post.objects.create(author=self.user2, title='Test Post', content='Content here')
        create_notification(recipient=self.user1, actor=self.user2, verb='liked', target=post)

        response = self.client.get(reverse('notification-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['notifications']), 1)
        self.assertEqual(response.data['unread_count'], 1)  # Assuming the default is unread
