import os
from django.conf import settings
from rest_framework import serializers
from image.models import Image


class ImageUpdateListDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Image
        fields = ['id', 'user', 'file_name', 'file_size', 'file_path', 'upload_date', 'mime_type', 
                  'description', 'tags', 'genre',]
        read_only_fields = [
            'id', 'user', 'file_size', 'upload_date', 'mime_type', 
            'duration', 'resolution', 'frame_rate',
        ]

class ImageCreateSerializer(serializers.ModelSerializer):
    image_file = serializers.FileField(write_only=True, required=True)
    
    
    ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg']
    MAX_FILE_SIZE = 50 * 1024 * 1024 # Máximo de 50MB
    class Meta:
        model = Image
        fields = ['description', 'tags', 'genre', 'image_file']
    
    def validate_iamge_file(self, value):
        image_type = value.content_type
        image_size = value.size
        
        if image_type not in self.ALLOWED_TYPES:
            raise serializers.ValidationError({'detail': f"Formato de imagem não permitido. Tipos aceitos: PNG, JPEG, JPG"})
        
        if image_size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError({'detail': 'Tamanho do arquivo não pode ser maior que 50MB.'})
        
        return value

class ImagePartialUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Image
        fields = ['description', 'tags', 'genre', 'file_name']
