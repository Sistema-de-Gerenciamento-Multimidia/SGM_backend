from django.db.utils import IntegrityError
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from users.serializers import CustomUserCreateSerializer, CustomUserUpdateListDetailSerializer, ChangeUserPasswordSerializer
from users.models import CustomUser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .permissions import IsUserOrAdmin
from video.models import Video
from video.serializers import VideoUpdateListDetailSerializer
from audio.models import Audio
from audio.serializers import AudioUpdateListDetailSerializer


class UserCRUDView(viewsets.ModelViewSet):
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
        
        if self.action in ['retrieve', 'partial_update', 'update']:
            permission_classes = [IsUserOrAdmin]
        elif self.action in ['list', 'destroy']:
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
    
    @action(detail=True, methods=['GET'], url_path="all-media") 
    def get_all_media_files(self, request, pk=None):
        try:
            user = self.get_object()
            
            user_videos = Video.objects.filter(user=user).all()
            user_audios = Audio.objects.filter(user=user).all()
            
            video_serializer = VideoUpdateListDetailSerializer(user_videos, many=True)
            audio_serializer = AudioUpdateListDetailSerializer(user_audios, many=True)
            
            response_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                },
                'videos': video_serializer.data,
                'audios': audio_serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangeUserPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        
        # Quando é um admin alterando a senha do usuário
        if self.request.user.is_staff and user_id:
            user = CustomUser.objects.filter(id=user_id).first()
        # Quando é o próprio usuário alterando a senha
        elif user_id == self.request.user.id:
            user = request.user
        else:
            return Response(
                data={'message': 'Você não tem permissão para realiza essa ação.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangeUserPasswordSerializer(data=request.data, context={'request': request, 'user': user})
        serializer.is_valid(raise_exception=True)
        
        serializer.update(user, serializer.validated_data)
        
        return Response(
            data={'message': 'Senha atualizada com sucesso.'},
            status=status.HTTP_200_OK,
        )
