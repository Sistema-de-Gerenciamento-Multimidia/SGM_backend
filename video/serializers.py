import os
from django.conf import settings
from rest_framework import serializers
from video.models import Video


class VideoUpdateListDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Video
        fields = ['id', 'user', 'file_name', 'file_size', 'file_path', 'upload_date', 'mime_type', 
                  'duration', 'resolution', 'frame_rate', 'video_codec', 'audio_codec',
                  'bitrate', 'thumbnail_path', 'processing_details', 'description', 'tags',
                  'genre',]
        read_only_fields = [
            'id', 'user', 'file_size', 'upload_date', 'mime_type', 
            'duration', 'resolution', 'frame_rate', 'video_codec', 'audio_codec',
            'bitrate', 'thumbnail_path', 'processing_details'
        ]

class VideoCreateSerializer(serializers.ModelSerializer):
    video_file = serializers.FileField(write_only=True, required=True)
    
    
    ALLOWED_TYPES = ['video/mp4', 'video/avi', 'video/quicktime', 'video/webm']
    MAX_FILE_SIZE = 50 * 1024 * 1024 # Máximo de 50MB
    class Meta:
        model = Video
        fields = ['description', 'tags', 'genre', 'video_file']
    
    def validate_video_file(self, value):
        video_type = value.content_type
        video_size = value.size
        
        if video_type not in self.ALLOWED_TYPES:
            raise serializers.ValidationError({'detail': f"Formato de vídeo não permitido. Tipos aceitos: MP4, AVI, MOV, WEBM"})
        
        if video_size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError({'detail': 'Tamanho do arquivo não pode ser maior que 50MB.'})
        
        return value

class VideoPartialUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Video
        fields = ['description', 'tags', 'genre', 'file_name']
