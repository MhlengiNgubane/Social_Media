import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from chat.models import Chat

User = get_user_model()

@pytest.mark.django_db
class ChatTest(APITestCase):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass1')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass2')
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        # Alternatively, if using session auth:
        self.client.login(username='user1', password='testpass1')

    def test_create_chat_message(self):
        url = reverse('chat-list')
        data = {
            'recipient': self.user2.id,
            'content': 'Hello, this is a test message',
        }
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_inbox_view(self):
        # Create a chat message sent to user1
        Chat.objects.create(sender=self.user2, recipient=self.user1, content='Test message to inbox')

        url = reverse('chat-inbox')  # 'chat-inbox' corresponds to the 'inbox' action
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test message to inbox')

    def test_sent_view(self):
        # Create a chat message sent by user1
        Chat.objects.create(sender=self.user1, recipient=self.user2, content='Test message sent')

        url = reverse('chat-sent')  # 'chat-sent' corresponds to the 'sent' action
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test message sent')

    def test_conversation_view(self):
        # Create conversation messages between user1 and user2
        Chat.objects.create(sender=self.user1, recipient=self.user2, content='Message 1 from user1')
        Chat.objects.create(sender=self.user2, recipient=self.user1, content='Message 2 from user2')

        url = reverse('chat-conversation', kwargs={'recipient_id': self.user2.id})  # 'chat-conversation' corresponds to the 'conversation' action
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], 'Message 1 from user1')
        self.assertEqual(response.data[1]['content'], 'Message 2 from user2')
