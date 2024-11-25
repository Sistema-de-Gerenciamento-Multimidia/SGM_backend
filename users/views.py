from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, viewsets
from users.serializers import UserListDetailSerializer
from users.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class UserListView(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserListDetailSerializer(queryset, many=True)
        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserListDetailSerializer(user)
        return Response(serializer.data)
    
    
    def create(self, request):
        ...


