from django.contrib import admin
from django.urls import path
from users.views import UserListView


urlpatterns = [
    path('users/', UserListView.as_view({'get': 'list'}), name='user-list-view'),
    path('users/<int:pk>/', UserListView.as_view({'get': 'retrieve'}), name='user-retrieve-view'),
]