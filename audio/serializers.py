from rest_framework import serializers
from audio.models import Audio


class AudioUpdateListDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Audio
        fields = ('id', 'user', 'file_name', 'file_size', 'mime_type', 'file_path', 'duration',
                  'bitrate', 'sample_rate', 'channels', 'description', 'tags', 'genre')
        read_only_fields = [
            'id', 'user', 'file_size', 'mime_type', 'file_path', 'duration', 'bitrate',
            'sample_rate', 'channels',
        ]

class AudioCreateSerializer(serializers.ModelSerializer):
    audio_file = serializers.FileField(write_only=True, required=True)
    
    ALLOWED_TYPES = ('audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac')
    MAX_FILE_SIZE = 50 * 1024 * 1024 # Máximo de 50MB
    
    class Meta:
        model = Audio
        fields = ('audio_file', 'description', 'tags', 'genre')
        
    def validate_audio_file(self, value):
        audio_type = value.content_type
        audio_size = value.size
        
        if audio_type not in self.ALLOWED_TYPES:
            raise serializers.ValidationError({'detail': f"Formato de áudio não permitido. Tipos aceitos: MP3, WAV, OGG, FLAC."})
        
        if audio_size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError({'detail': 'Tamanho do arquivo não pode ser maior que 50MB.'})
        
        return value

class AudioPartialUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Audio
        fields = ('description', 'tags', 'file_name')
