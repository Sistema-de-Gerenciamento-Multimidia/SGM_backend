import os
import subprocess
from botocore.exceptions import BotoCoreError, NoCredentialsError
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import viewsets, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from app.services.aws_services import aws_services
from audio.permissions import IsUserOrAdmin
from app.services.audio_services import (
    extract_audio_info,
    save_video_in_temporary_file,
    remove_video_in_temporary_file
)
from app.utils.s3_utils import extract_s3_key
from audio.models import Audio
from audio.serializers import AudioCreateSerializer, AudioUpdateListDetailSerializer, AudioPartialUpdateSerializer


class AudioCRUDView(viewsets.ModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioUpdateListDetailSerializer
    permission_classes = [AllowAny]
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AudioCreateSerializer
        elif self.request.method == "PATCH":
            return AudioPartialUpdateSerializer
        else:
            return AudioUpdateListDetailSerializer
    
    def get_permissions(self):
        permission_classes = self.permission_classes
        
        if self.action in ['retrieve', 'partial_update', 'update', 'destroy', 'create', 'list']:
            permission_classes = [IsUserOrAdmin]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            audio_file = serializer.validated_data.get('audio_file')
            audio_file_name = audio_file.name
            audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio_files', audio_file_name)
            
            os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
            save_video_in_temporary_file(audio_file, audio_file_path)
            
            # Salva o arquivo de áudio no bucket
            s3_audio_path = aws_services.upload_audio_to_s3(audio_file_name, audio_file_path, self.request.user.id)
            
            audio_metadata = extract_audio_info(audio_file_path)
            
            
            with transaction.atomic():
                audio_instance = Audio.objects.create(
                    file_name=audio_file_name,
                    file_size=audio_file.size,
                    mime_type=audio_file.content_type,
                    file_path=s3_audio_path,
                    **audio_metadata,
                    description=serializer.validated_data.get('description', ''),
                    tags=serializer.validated_data.get('tags', []),
                    genre=serializer.validated_data.get('genre', ''),
                    user=self.request.user,
                )
            
            return Response(
                data=AudioUpdateListDetailSerializer(audio_instance).data,
                status=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos. Verifique e tente novamente'}, status=status.HTTP_400_BAD_REQUEST)

        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload do áudio para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o áudio. Verifique os dados e tente novamente.'}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento do áudio'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de áudio não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            remove_video_in_temporary_file(audio_file_path)
            
    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            all_audios = Audio.objects.filter(user=user).all()
            if not all_audios:
                raise Response(
                    data={'detail': "Nenhum áudio foi encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
            serializer = AudioUpdateListDetailSerializer(instance=all_audios, many=True)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos. Verifique e tente novamente'}, status=status.HTTP_400_BAD_REQUEST)

        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload do áudio para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o áudio. Verifique os dados e tente novamente.'}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento do áudio'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de áudio não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            audio_id = self.kwargs.get('pk')
            audio_object = Audio.objects.filter(id=audio_id, user=self.request.user).first()
            if not audio_object:
                raise ValueError('Vídeo não encontrado.')
        
            serializer = AudioUpdateListDetailSerializer(instance=audio_object)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos. Verifique e tente novamente'}, status=status.HTTP_400_BAD_REQUEST)

        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload do áudio para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o áudio. Verifique os dados e tente novamente.'}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento do áudio'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de áudio não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def update(self, request, *args, **kwargs):
        return Response(
            data={'detail': 'Método Update não é permitido'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
        
    def partial_update(self, request, *args, **kwargs):
        # try:
            # Obtendo o vídeo existente
            audio_instance = self.get_object()
            if not audio_instance:
                raise ValueError('Vídeo não encontrado.')

            # Valida os dados recebidos no request
            serializer = self.get_serializer(audio_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Atualizando o campo file_name
            if 'file_name' in serializer.validated_data:
                new_file_name = serializer.validated_data['file_name']
                
                local_download_old_audio_path = os.path.join(settings.MEDIA_ROOT, 'audio_files', audio_instance.file_name)
                # Baixa o arquivo já existente no s3
                aws_services.download_audio_from_s3(extract_s3_key(audio_instance.file_path), local_download_old_audio_path)
                
                # Define o novo caminho do arquivo com o novo nome
                new_file_path = os.path.join(settings.MEDIA_ROOT, 'audio_files', new_file_name)
                
                # Renomeia o arquivo
                os.rename(local_download_old_audio_path, new_file_path)
                
                # Faz o upload do arquivo renomeado para o S3
                new_s3_path = aws_services.upload_audio_to_s3(new_file_name, new_file_path, self.request.user.id)

                aws_services.delete_object_from_s3(extract_s3_key(audio_instance.file_path))
                
                # Atualiza os dados da instância no banco de dados
                audio_instance.file_name = new_file_name
                audio_instance.file_path = new_s3_path
                
                # Extraindo os metadados atualizados do novo arquivo
                audio_metadata = extract_audio_info(new_file_path)
                audio_instance.duration = audio_metadata.get('duration')
                audio_instance.bitrate = audio_metadata.get('bitrate')
                audio_instance.sample_rate = audio_metadata.get('sample_rate')
                audio_instance.channels = audio_metadata.get('channels')
            
            # Atualiza outros campos permitidos (tags, description)
            if 'tags' in serializer.validated_data:
                audio_instance.tags = serializer.validated_data['tags']

            if 'description' in serializer.validated_data:
                audio_instance.description = serializer.validated_data['description']
                
            # Salva as alterações no banco de dados
            audio_instance.save()
            
            os.remove(new_file_path)

            return Response(
                data=AudioUpdateListDetailSerializer(audio_instance).data,
                status=status.HTTP_200_OK
            )
        
        # except ValueError:
        #     return Response({'detail': 'Áudio não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # except NoCredentialsError:
        #     return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # except BotoCoreError as e:
        #     return Response({'detail': 'Erro ao fazer upload do áudio para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # except IntegrityError:
        #     return Response({'detail': 'Erro ao salvar o áudio. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        # except subprocess.CalledProcessError:
        #     return Response({'detail': 'Erro durante o processamento do áudio'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # except FileNotFoundError as e:
        #     return Response({'detail': f'Arquivo de áudio não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # except Exception as e:
        #     return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def destroy(self, request, *args, **kwargs):
        try:
            
            audio_id = self.kwargs.get('pk')
            audio_object = Audio.objects.filter(id=audio_id, user=self.request.user).first()
            if not audio_object:
                raise ValueError('Vídeo não encontrado.')
            
            # Remove thumbnail
            aws_services.delete_object_from_s3(extract_s3_key(audio_object.file_path))
            
            return super().destroy(request, *args, **kwargs)
        
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos. Verifique e tente novamente'}, status=status.HTTP_400_BAD_REQUEST)

        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload do áudio para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o áudio. Verifique os dados e tente novamente.'}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento do áudio'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de áudio não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
