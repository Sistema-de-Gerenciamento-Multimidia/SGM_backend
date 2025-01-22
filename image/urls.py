from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from image.views import ImageCRUDView


router = DefaultRouter()
router.register(r'images', ImageCRUDView, basename='image')

urlpatterns = [
    path('', include(router.urls)),
]

