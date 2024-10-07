from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatViewSet

router = DefaultRouter()
router.register(r'chat', ChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
