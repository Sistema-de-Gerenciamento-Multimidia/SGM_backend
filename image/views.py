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
from image.permissions import IsUserOrAdmin
from app.utils.s3_utils import extract_s3_key
from image.models import Image
from image.serializers import ImageUpdateListDetailSerializer, ImageCreateSerializer


class ImageCRUDView(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageUpdateListDetailSerializer
    permission_classes = [AllowAny]
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ImageCreateSerializer
        
        else:
            return ImageUpdateListDetailSerializer
    
    def get_permissions(self):
        permission_classes = self.permission_classes
        
        if self.action in ['retrieve', 'partial_update', 'update', 'destroy', 'create', 'list']:
            permission_classes = [IsUserOrAdmin]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            image_file = serializer.validated_data.get('image_file')
            image_file_name = image_file.name
            image_file_path = os.path.join(settings.MEDIA_ROOT, 'image_files', image_file_name)
            
            os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
            save_image_in_temporary_file(image_file, image_file_path)
            
            # Processamento do vídeo em diferentes qualidades
            processed_images = process_image_qualities(image_file_path)
            processed_image_paths = {}
            
            for quality, processed_image in processed_images.items():
                s3_path = aws_services.upload_image_to_s3(processed_image.split(os.sep)[-1], processed_image, self.request.user.id)
                processed_image_paths[quality] = s3_path
                remove_image_in_temporary_file(processed_image)
            
            metadata = extract_image_info(image_file_path)
            
            with transaction.atomic():
                image_instance = Image.objects.create(
                    file_name=image_file_name,
                    file_size=image_file.size,
                    mime_type=image_file.content_type,
                    file_path=processed_image_paths['1080p'],
                    processing_details=processed_image_paths,
                    description=serializer.validated_data.get('description', ''),
                    tags=serializer.validated_data.get('tags', []),
                    genre=serializer.validated_data.get('genre', ''),
                    user=self.request.user,
                    **metadata
                )
            
            return Response(
                data=ImageUpdateListDetailSerializer(image_instance).data,
                status=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos. Verifique e tente novamente'}, status=status.HTTP_400_BAD_REQUEST)

        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload do vídeo para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar o vídeo. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento da imagem'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de vídeo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            remove_video_in_temporary_file(video_file_path)
    
    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            all_videos = Video.objects.filter(user=user).all()
            if not all_videos:
                raise ValueError('Nenhum vídeo foi encontrado.')
        
            serializer = VideoUpdateListDetailSerializer(instance=all_videos, many=True)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        
        except ValueError:
            return Response({'detail': 'Vídeo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload da imagem para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento da imagem'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de imagem não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            image_id = self.kwargs.get('pk')
            image_object = Image.objects.filter(id=image_id, user=self.request.user).first()
            if not image_object:
                raise ValueError('Imagem não encontrado.')
        
            serializer = ImageUpdateListDetailSerializer(instance=image_object)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        
        except ValueError:
            return Response({'detail': 'Imagem não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload da imagem para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento da imagem'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de imagem não encontrado. '}, status=status.HTTP_404_NOT_FOUND)

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
            image_instance = self.get_object()
            if not image_instance:
                raise ValueError('Vídeo não encontrado.')

            # Valida os dados recebidos no request
            serializer = self.get_serializer(image_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Atualizando o campo file_name
            if 'file_name' in serializer.validated_data:
                image_instance.file_name = serializer.validated_data['file_name']
            
            # Atualizando os outros campos permitidos (tags, description, genre)
            if 'tags' in serializer.validated_data:
                image_instance.tags = serializer.validated_data['tags']
            
            if 'description' in serializer.validated_data:
                image_instance.description = serializer.validated_data['description']
            
            if 'genre' in serializer.validated_data:
                image_instance.genre = serializer.validated_data['genre']


            # Salva as alterações no banco de dados
            image_instance.save()

            return Response(
                data=VideoUpdateListDetailSerializer(image_instance).data,
                status=status.HTTP_200_OK
            )
        
        except ValueError:
            return Response({'detail': 'Imagem não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload da imagem para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento da imagem.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # except FileNotFoundError as e:
        #     return Response({'detail': f'Arquivo de vídeo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # except Exception as e:
        #     return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def destroy(self, request, *args, **kwargs):
        try:
            
            image_id = self.kwargs.get('pk')
            image_object = Image.objects.filter(id=image_id, user=self.request.user).first()
            if not image_object:
                raise ValueError('Imagem não encontrado.')
            
            # Remove thumbnail
            aws_services.delete_object_from_s3(extract_s3_key(image_object.thumbnail_path))
            
            # Remove arquivos de vídeos processados
            for _, value in image_object.processing_details.items():
                aws_services.delete_object_from_s3(extract_s3_key(value))
            
            return super().destroy(request, *args, **kwargs)
        
        except ValueError:
            return Response({'detail': 'Imagem não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        except NoCredentialsError:
            return Response({'detail': 'Erro ao acessar o S3: credenciais ausentes.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except BotoCoreError as e:
            return Response({'detail': 'Erro ao fazer upload da imagem para o S3.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except subprocess.CalledProcessError:
            return Response({'detail': 'Erro durante o processamento doa imagem'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de imagem não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde. '}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    