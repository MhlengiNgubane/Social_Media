from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Comment, Hashtag, Like, Post

User = get_user_model()

class PostsTest(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='testpass1', email='testuser1@example.com')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2', email='testuser2@example.com')

        self.client.force_authenticate(user=self.user1)
        self.post_url = reverse('post-list')  # URL for listing and creating posts

    def test_create_post(self):
        url = reverse('post-list')
        data = {
            'title': 'New Test Post',
            'content': 'This is the content of the new post.',
            'hashtags': [{'name': 'testhashtag1'}, {'name': 'testhashtag2'}],
            'tagged_users': []
        }

        response = self.client.post(url, data, format='json')

        if response.status_code != status.HTTP_201_CREATED:
            print("Response status code:", response.status_code)
            print("Response data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_read_post(self):
        post = Post.objects.create(author=self.user1, title='Test Post', content='This is the content of the test post.')
        url = reverse('post-detail', args=[post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_update_post(self):
        post = Post.objects.create(author=self.user1, title='Original Title', content='Original content.')
        url = reverse('post-detail', args=[post.id])
        data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
            'hashtags': [{'name': 'updatedhashtag'}],
            'tagged_users': []
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, 'Updated Title')

    def test_delete_post(self):
        post = Post.objects.create(author=self.user1, title='Post to be deleted', content='Content of the post to be deleted.')
        url = reverse('post-detail', args=[post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_like_post(self):
        post = Post.objects.create(author=self.user1, title='Post to like', content='Content to like.')
        url = reverse('like-list')  # Assuming there's a like endpoint
        response = self.client.post(url, {'post_id': post.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_post(self):
        # Create a post to like
        post = Post.objects.create(author=self.user1, title='Test Post', content='This is a post for liking')
        
        # Like the post
        like_response = self.client.post(reverse('like-list'), {'post_id': post.id})  # Adjust if needed based on your view implementation
        self.assertEqual(like_response.status_code, status.HTTP_201_CREATED)

        # Ensure the like response contains the ID of the like
        self.assertIn('id', like_response.data)

        # Get the like ID from the response
        like_id = like_response.data['id']
        
        # Now unlike the post
        unlike_response = self.client.delete(reverse('like-detail', args=[like_id]))  # Delete the like
        self.assertEqual(unlike_response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the like no longer exists
        with self.assertRaises(Like.DoesNotExist):
            Like.objects.get(id=like_id)

    def test_comment_on_post(self):
        post = Post.objects.create(author=self.user1, title='Test Post', content='This is a post for commenting')
        url = reverse('comment-list')  # Ensure this matches your URL configuration
        data = {
            'post': post.id,
            'content': 'This is a comment.'
        }

        response = self.client.post(url, data, format='json')

        if response.status_code != status.HTTP_201_CREATED:
            print("Response status code:", response.status_code)
            print("Response data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_repost(self):
        original_post = Post.objects.create(author=self.user1, title='Original Post', content='Content of the original post.')
        url = reverse('repost', args=[original_post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)  # Ensure repost is created

    def test_create_post_with_invalid_data(self):
        data = {
            'title': '',  # Empty title
            'content': 'Content without a title.',
            'hashtags': [],
            'tagged_users': []
        }
        response = self.client.post(self.post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 0)  # No posts should be created
