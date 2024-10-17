from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()

class UserTest(APITestCase):
    def setUp(self):
        # Create two users: one for testing and another to follow
        self.user1 = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        self.user2 = User.objects.create_user(
            username='followuser',
            password='followpassword',
            email='followuser@example.com'
        )

        # Login user1 to obtain a token for authenticated requests
        self.token_url = reverse('login')  # Adjust the URL name as needed
        self.token_response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.token = self.token_response.data['token']

    def test_user_registration_success(self):
        url = reverse('register')  # Ensure this matches your URL name
        data = {
            'full_name': 'Test User',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_duplicate_username(self):
        url = reverse('register')
        data = {
            'full_name': 'Another User',
            'username': 'testuser',  # Existing username
            'email': 'anotheruser@example.com',
            'password': 'anotherpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        url = reverse('register')
        data = {
            'full_name': 'Another User',
            'username': 'anotheruser',
            'email': 'testuser@example.com',  # Existing email
            'password': 'anotherpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',  # Invalid password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_non_existent_user(self):
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'somepassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_detail_view(self):
        url = reverse('user-detail', args=[self.user1.id])  # Use self.user1.id instead of self.user.id
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)  # Check the returned data

    def test_follow_user_success(self):
        url = reverse('follow-user', args=[self.user2.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)  # Set authorization token
        response = self.client.post(url)

        # Assert that the follow operation was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if user1 is now in user2's followers
        self.assertTrue(self.user1.followers.filter(id=self.user2.id).exists(), "User1 should be in User2's followers.")
        self.assertIn(f'You are now following {self.user2.username}', response.data['message'])

    def test_unfollow_user_success(self):
        # First follow the user to set the stage for unfollowing
        self.user1.followers.add(self.user2)
        
        url = reverse('unfollow-user', args=[self.user2.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)  # Set authorization token
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user2.followers.filter(id=self.user1.id).exists())
        self.assertIn(f'You have unfollowed {self.user2.username}', response.data['message'])

    def test_following_yourself(self):
        url = reverse('follow-user', args=[self.user1.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)  # Set authorization token
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You cannot follow yourself.', response.data['message'])

    def test_following_non_existent_user(self):
        url = reverse('follow-user', args=[999])  # Non-existent user ID
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)  # Set authorization token
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follower_count_updates(self):
        # Initially, the follower count should be 0
        self.assertEqual(self.user2.followers.count(), 0)

        # Follow the user
        url = reverse('follow-user', args=[self.user2.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)  # Ensure we are authenticated
        follow_response = self.client.post(url)

        # Assert follow response status
        self.assertEqual(follow_response.status_code, status.HTTP_200_OK)

        # Check that the follower count increased
        self.assertEqual(self.user1.followers.count(), 1, "Follower count should be 1 after following.")

        # Unfollow the user
        url = reverse('unfollow-user', args=[self.user2.id])
        unfollow_response = self.client.post(url)

        # Assert unfollow response status
        self.assertEqual(unfollow_response.status_code, status.HTTP_200_OK)

        # Check that the follower count decreased
        self.assertEqual(self.user2.followers.count(), 0, "Follower count should be 0 after unfollowing.")
        
    def test_logout(self):
        # Ensure the user is authenticated before the logout
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)  # Set token in the header
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.user1.id}))  # Use self.user1.id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Now test the logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Successfully logged out.'})

        # Ensure the token no longer works for authenticated requests
        self.client.credentials()  # Remove the token from the headers
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.user1.id}))  # Use self.user1.id
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
