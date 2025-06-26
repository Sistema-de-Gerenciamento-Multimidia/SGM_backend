import os
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from video.permissions import IsUserOrAdmin
from app.utils import save_media, remove_media, generate_sha256_file_hash, is_file_duplicated
from app.tasks import process_upload_video
from video.models import Video
from video.serializers import VideoUpdateListDetailSerializer, VideoCreateSerializer


class VideoCRUDView(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoUpdateListDetailSerializer
    permission_classes = [AllowAny]
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VideoCreateSerializer
        
        else:
            return VideoUpdateListDetailSerializer
    
    def get_permissions(self):
        permission_classes = self.permission_classes
        
        if self.action in ['retrieve', 'partial_update', 'update', 'destroy', 'create', 'list']:
            permission_classes = [IsUserOrAdmin]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            video_file = serializer.validated_data.get('video_file')
            user_id = str(self.request.user.id)
            
            video_file_hash = generate_sha256_file_hash(video_file, self.request.user)
            if is_file_duplicated(video_file_hash, 'Video', self.request.user):
                return Response(
                    data={'detail': 'Arquivo já enviado anteriormente ao sistema.'},
                    status=status.HTTP_409_CONFLICT
                )
            
            
            # Definindo método de armazenamento dos arquivos de vídeo
            user_videos_folder = os.path.join(settings.MEDIA_ROOT, 'video_files', 'user', user_id)
            original_videos_folder = os.path.join(user_videos_folder, 'original')
            processed_videos_folder = os.path.join(user_videos_folder, 'processed')
            thumbnails_folder = os.path.join(user_videos_folder, 'thumbnails')
            
            os.makedirs(original_videos_folder, exist_ok=True)
            os.makedirs(processed_videos_folder, exist_ok=True)
            os.makedirs(thumbnails_folder, exist_ok=True)
            
            # Caminho do vídeo original
            video_file_name = video_file.name
            video_original_path = os.path.join(original_videos_folder, video_file_name)
            
            # Salva o arquivo original
            save_media(video_file, video_original_path)
            
            with transaction.atomic():
                video_instance = Video.objects.create(
                    file_name=video_file_name,
                    file_size=video_file.size,
                    file_hash=video_file_hash,
                    mime_type=video_file.content_type,
                    file_path=video_original_path,
                    description=serializer.validated_data.get('description', ''),
                    tags=serializer.validated_data.get('tags', []),
                    genre=serializer.validated_data.get('genre', ''),
                    user=self.request.user,
                    status=Video.PROCESSING
                )
            
            # Chamada do processamento assíncrono usando Celery
            process_upload_video(video_instance.id, video_original_path)
            
            return Response(
                data=VideoUpdateListDetailSerializer(video_instance).data,
                status=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos. Verifique e tente novamente'}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o vídeo. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de vídeo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            all_videos = Video.objects.filter(user=user).all()
            if not all_videos:
                return Http404({"detail": "Arquivo de vídeo não encontrado."})
        
            serializer = VideoUpdateListDetailSerializer(instance=all_videos, many=True)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o vídeo. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de vídeo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            video_id = self.kwargs.get('pk')
            video_object = Video.objects.filter(id=video_id, user=self.request.user).first()
            if not video_object:
                raise Http404({"detail": "Vídeo não encontrado."})
        
            serializer = VideoUpdateListDetailSerializer(instance=video_object)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        except PermissionDenied as fe:
            return Response({"detail": "Arquivo de vídeo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o vídeo. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de vídeo não encontrado. '}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        return Response(
            data={'detail': 'Método Update não é permitido'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
        
    def partial_update(self, request, *args, **kwargs):
        try:
            # Obtendo o vídeo existente
            video_instance = self.get_object()
            if not video_instance:
                raise Http404({"detail": "Vídeo não encontrado."})

            # Valida os dados recebidos no request
            serializer = self.get_serializer(video_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Atualizando o campo file_name
            if 'file_name' in serializer.validated_data:
                new_file_name = serializer.validated_data['file_name']
                _, file_extension = os.path.splitext(video_instance.file_name)
                new_file_name_with_ext = new_file_name + file_extension
                
                user_videos_folder = os.path.join(settings.MEDIA_ROOT, 'video_files', 'user', str(self.request.user.id))
                original_videos_folder = os.path.join(user_videos_folder, 'original')
                processed_videos_folder = os.path.join(user_videos_folder, 'processed')
                
                old_video_path = os.path.join(original_videos_folder, video_instance.file_name)
                new_video_path = os.path.join(original_videos_folder, new_file_name_with_ext)
                
                # Verifica se existe o arquivo original
                if os.path.exists(old_video_path):
                    os.rename(old_video_path, new_video_path)
                    video_instance.file_name = new_file_name_with_ext
                    video_instance.file_path = new_video_path
                    
                    for resolution in ['1080p', '720p', '480p']:
                        # Captura o nome antigo do vídeo processado
                        old_processed_video_file_name, ext = os.path.splitext(video_instance.processing_details[resolution])
                        old_processed_video_file_name_with_ext = f'{os.path.basename(old_processed_video_file_name)}{ext}'
                        new_processed_video_file_name = f'{new_file_name}_{resolution}{ext}'
                        
                        old_processed_video_path = os.path.join(processed_videos_folder, old_processed_video_file_name_with_ext)
                        new_processed_video_path = os.path.join(processed_videos_folder, new_processed_video_file_name)
                        
                        # Verifica se o vídeo processado existe
                        if os.path.exists(old_processed_video_path):
                            os.rename(old_processed_video_path, new_processed_video_path)
                            video_instance.processing_details[resolution] = new_processed_video_path
                        else:
                            return Response(
                                data={'detail': f'O vídeo processado em {resolution} não foi encontrado.'},
                                status=status.HTTP_404_NOT_FOUND
                            )
                else:
                    return Response(
                        data={'detail': 'Arquivo de vídeo original não encontrado.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Atualizando os outros campos permitidos (tags, description, genre)
            if 'tags' in serializer.validated_data:
                video_instance.tags = serializer.validated_data['tags']
            
            if 'description' in serializer.validated_data:
                video_instance.description = serializer.validated_data['description']

            # Salva as alterações no banco de dados
            video_instance.save()

            return Response(
                data=VideoUpdateListDetailSerializer(video_instance).data,
                status=status.HTTP_200_OK
            )

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o vídeo. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)
        
        except OSError as ose:
            #logger.error(ose)
            return Response({'detail': 'Erro durante o processo de alteração do nome do arquivo de vídeo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de vídeo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except PermissionDenied as fe:
            return Response({"detail": "Arquivo de vídeo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def destroy(self, request, *args, **kwargs):
        try:
            
            video_id = self.kwargs.get('pk')
            video_object = Video.objects.filter(id=video_id, user=self.request.user).first()
            if not video_object:
                raise Http404({"detail": 'Vídeo não encontrado.'})

            remove_media(video_object.file_path)
            
            return super().destroy(request, *args, **kwargs)

        except PermissionDenied as fe:
            return Response({"detail": "Arquivo de vídeo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o vídeo. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': 'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['GET'], url_path='status', permission_classes=[IsUserOrAdmin])
    def get_video_status(self, request, *args, **kwargs):
        try:
            video = self.get_object()
            if not video:
                raise Http404({"detail": "Vídeo não encontrado."})
            
            return Response(
                data={'status': video.status},
                status=status.HTTP_200_OK
            )

        except PermissionDenied as fe:
            return Response({"detail": "Arquivo de vídeo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'detail': 'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)