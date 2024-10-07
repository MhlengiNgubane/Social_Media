from django.urls import path

from .views import (LoginView, ProfileViewSet, RegisterView, UserDetailView,
                    follow_user, unfollow_user)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('follow/<int:user_id>/', follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', unfollow_user, name='unfollow-user'),
    path('user/<int:user_id>/profile/', ProfileViewSet.as_view({'get': 'retrieve'}), name='user-profile'),  # User profile
]
