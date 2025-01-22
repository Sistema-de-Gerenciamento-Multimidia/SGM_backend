from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from video.views import VideoCRUDView


router = DefaultRouter()
router.register(r'videos', VideoCRUDView, basename='video')

urlpatterns = [
    path('', include(router.urls)),
]

