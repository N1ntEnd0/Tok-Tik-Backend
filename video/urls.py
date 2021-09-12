from django.urls import path
from rest_framework.routers import DefaultRouter

from video.views import VideoViewSet

urlpatterns = [
]
router = DefaultRouter()
router.register('', VideoViewSet, basename='video')
urlpatterns += router.urls