import os
import subprocess
from botocore.exceptions import BotoCoreError, NoCredentialsError
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404
from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from image.permissions import IsUserOrAdmin
from app.services.image_services import extract_image_info
from app.utils import save_image, generate_sha256_file_hash, is_file_duplicated, remove_media
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
            image_file_path = os.path.join(settings.MEDIA_ROOT, 'image', image_file_name)
            image_file_hash = generate_sha256_file_hash(image_file, self.request.user)
            
            if is_file_duplicated(image_file_hash, 'Image', self.request.user):
                return Response(
                    data={'detail': 'Arquivo já enviado anteriormente ao sistema.'},
                    status=status.HTTP_409_CONFLICT
                )
            
            os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
            save_image(image_file, image_file_path)
            
            # Processamento da imagem para retornar suas propriedades específicas
            image_info = extract_image_info(image_file_path)
            
            with transaction.atomic():
                image_instance = Image.objects.create(
                    file_name=image_file_name,
                    file_hash=image_file_hash,
                    file_size=image_file.size,
                    mime_type=image_file.content_type,
                    file_path=image_file_path,
                    dimensions=image_info.get('Dimensions', None),
                    color_depth=image_info.get('ColorDepth', None),
                    resolution=image_info.get('DPI', None),
                    exif_metadata=image_info.get('Exif', None),
                    description=serializer.validated_data.get('description', None),
                    tags=serializer.validated_data.get('tags', []),
                    user=self.request.user,
                )
            
            return Response(
                data=ImageUpdateListDetailSerializer(image_instance).data,
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
            all_images = Image.objects.filter(user=user).all()
            if not all_images:
                raise ValueError('Nenhum vídeo foi encontrado.')
        
            serializer = ImageUpdateListDetailSerializer(instance=all_images, many=True)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)
        
        except FileNotFoundError as e:
            return Response({'detail': f'Arquivo de imagem não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            image_id = self.kwargs.get('pk')
            image_object = Image.objects.filter(id=image_id, user=self.request.user).first()
            if not image_object:
                raise Http404({'detail': "Arquivo de imagem não encontrado."})
        
            serializer = ImageUpdateListDetailSerializer(instance=image_object)
            
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        except PermissionDenied as pe:
            return Response({'detail': "Arquivo de imagem não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        except IntegrityError as ie:
            return Response({'detail': "Erro ao salvar a imagem. Verifique os dados e tente novamente."}, sttaus=status.HTTP_404_NOT_FOUND)
        
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
            # Obtendo a imagem existente
            image_instance = self.get_object()
            if not image_instance:
                raise Http404({"detail": "Imagem não encontrada."})

            # Valida os dados recebidos no request
            serializer = self.get_serializer(image_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Atualizando o campo file_name
            if 'file_name' in serializer.validated_data:
                new_file_name = serializer.validated_data['file_name']
                
                _, file_extension = os.path.splitext(image_instance.file_name)
                new_file_name_with_ext = new_file_name + file_extension
                
                old_image_path = os.path.join(settings.MEDIA_ROOT, 'image', image_instance.file_name)
                new_image_path = os.path.join(settings.MEDIA_ROOT, 'image', new_file_name_with_ext)

                # Verifica se o arquivo original existe antes de renomear
                if os.path.exists(old_image_path):
                    os.rename(old_image_path, new_image_path)
                    image_instance.file_name = new_file_name_with_ext
                    image_instance.file_path = new_image_path
                else:
                    return Response(
                        data={'detail': 'Arquivo original não encontrado.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
            # Atualizando os outros campos permitidos (tags, description, genre)
            if 'tags' in serializer.validated_data:
                image_instance.tags = serializer.validated_data['tags']
            
            if 'description' in serializer.validated_data:
                image_instance.description = serializer.validated_data['description']

            # Salva as alterações no banco de dados
            image_instance.save()

            return Response(
                data=ImageUpdateListDetailSerializer(image_instance).data,
                status=status.HTTP_200_OK
            )

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)
        
        except OSError as ose:
            #logger.error(ose)
            return Response({'detail': 'Erro durante o processo de alteração do arquivo de imagem.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except FileNotFoundError as fnfe:
            return Response({'detail': f'Arquivo de imagem não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        except PermissionDenied as pe:
            return Response({'detail': 'Arquivo de imagem não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def destroy(self, request, *args, **kwargs):
        try:
            
            image_id = self.kwargs.get('pk')
            image_object = Image.objects.filter(id=image_id, user=self.request.user).first()
            if not image_object:
                raise Http404({'detail': 'Imagem não encontrada.'})
            
            # Remove a imagem do diretório de imagens
            remove_media(image_object.file_path)
            
            return super().destroy(request, *args, **kwargs)

        except PermissionDenied as pe:
            return  Response({'detail': 'Arquivo de vídeo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError:
            return Response({'detail': 'Erro ao salvar a imagem. Verifique os dados e tente novamente. '}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': f'Ocorreu um erro inesperado. Tente novamente mais tarde. '}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    