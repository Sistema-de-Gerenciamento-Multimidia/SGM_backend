from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserListView, ChangeUserPasswordView

router = DefaultRouter()
router.register(r'users', UserListView, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('change-password/<int:user_id>', ChangeUserPasswordView.as_view(), name='change-user-password')
]