from django.db.utils import IntegrityError
from rest_framework import viewsets, serializers, status
from rest_framework.views import APIView
from users.serializers import CustomUserCreateSerializer, CustomUserUpdateListDetailSerializer, ChangeUserPasswordSerializer
from users.models import CustomUser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


class UserListView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserUpdateListDetailSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        else:
            return CustomUserUpdateListDetailSerializer
    
    def get_permissions(self):
        permission_classes = self.permission_classes
        
        if self.action in ['retrieve', 'update']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser, IsAuthenticated]
        elif self.action in ['create']:
            permission_classes = [AllowAny]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()
            
            headers = self.get_success_headers(data=serializer.data)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'Erro ao salvar o usuário. Verifique os dados e tente novamente.'})

class ChangeUserPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        
        # Quando é um admin alterando a senha do usuário
        if self.request.user.is_staff and user_id:
            user = CustomUser.objects.filter(id=user_id).first()
        # Quando é o próprio usuário alterando a senha
        else:
            user = request.user
        
        serializer = ChangeUserPasswordSerializer(data=request.data, context={'request': request, 'user': user})
        serializer.is_valid(raise_exception=True)
        
        serializer.update(user, serializer.validated_data)
        
        return Response(
            data={'message': 'Senha atualizada com sucesso.'},
            status=status.HTTP_200_OK,
        )
