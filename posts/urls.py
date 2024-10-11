from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CommentViewSet, FeedViewSet, HashtagViewSet, LikeViewSet,
                    PostViewSet, RepostViewSet, SuggestionViewSet,
                    TrendingPostsViewSet)

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')  # Likes endpoint
router.register(r'feed', FeedViewSet, basename='feed')  # User feed endpoint
router.register(r'suggestions', SuggestionViewSet, basename='suggestions')  # User suggestions endpoint
router.register(r'reposts', RepostViewSet, basename='reposts')

urlpatterns = [
    path('', include(router.urls)),
    path('likes/<int:pk>/', LikeViewSet.as_view({'delete': 'destroy'}), name='like-detail'),
    path('posts/<int:post_id>/repost/', RepostViewSet.as_view({'post': 'create'}), name='repost'),
    path('trending/', TrendingPostsViewSet.as_view({'get': 'list'}), name='trending-posts'),
]
