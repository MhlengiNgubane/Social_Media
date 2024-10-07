from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CommentViewSet, FeedViewSet, HashtagViewSet, LikeViewSet,
                    PostViewSet, RepostViewSet, SuggestionViewSet,
                    TrendingPostsViewSet)

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'posts', PostViewSet)  # Posts endpoint
router.register(r'comments', CommentViewSet)  # Comments endpoint
router.register(r'likes', LikeViewSet, basename='like')  # Likes endpoint
router.register(r'feed', FeedViewSet, basename='feed')  # User feed endpoint
router.register(r'suggestions', SuggestionViewSet, basename='suggestions')  # User suggestions endpoint
router.register(r'reposts', RepostViewSet, basename='reposts')

urlpatterns = [
    path('', include(router.urls)),
    path('post/<int:post_id>/repost/', RepostViewSet.as_view({'post': 'create'}), name='repost'),
    path('hashtags/<str:hashtag_name>/', HashtagViewSet.as_view({'get': 'list'}), name='hashtag-posts'),
    path('trending/', TrendingPostsViewSet.as_view({'get': 'list'}), name='trending-posts'),
]
