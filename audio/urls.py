from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from audio.views import AudioCRUDView


router = DefaultRouter()
router.register(r'audios', AudioCRUDView, basename='audio')

urlpatterns = [
    path('', include(router.urls)),
]

