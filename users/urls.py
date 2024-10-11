from django.urls import path

from .views import (FollowUserView, LoginView, ProfileViewSet, RegisterView,
                    UnfollowUserView, UserDetailView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('profile/<int:user_id>/', ProfileViewSet.as_view({'get': 'retrieve'}), name='profile-detail'),
]
