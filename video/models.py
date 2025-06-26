from django.db import models
from users.models import CustomUser


class Video(models.Model):
    PROCESSING = 0
    COMPLETED = 1
    STATUS_CHOICES = [
        (PROCESSING, 'Processando'),
        (COMPLETED, 'Completo'),
    ]
    
    file_name = models.CharField(max_length=255, null=False, blank=False)
    file_size = models.BigIntegerField() # In bytes
    file_hash = models.CharField(max_length=255, unique=True, null=False, blank=False) # Nome único do arquivo salvo no servidor para controle de duplicações
    upload_date = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255, null=False, blank=False, unique=True)
    
    duration = models.FloatField(null=True, blank=True) # Video duration in seconds
    resolution = models.CharField(max_length=255, null=True, blank=True) # Ex: "1920x1080"
    frame_rate = models.FloatField(null=True, blank=True)
    video_codec = models.CharField(max_length=255, null=True, blank=True)
    audio_codec = models.CharField(max_length=255, null=True, blank=True)
    bitrate = models.IntegerField(null=True, blank=True) # Bitrate in kbps
    
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PROCESSING, null=False, blank=False)
    
    thumbnail_path = models.CharField(max_length=255)
    
    processing_details = models.JSONField(default=dict)
    # Exemplo de Estrutura:
    # {
    #     "1080p": "path/to/video_1080p.mp4",
    #     "720p": "path/to/video_720p.mp4",
    #     "480p": "path/to/video_480p.mp4",
    # }
    
    description = models.TextField(null=True, blank=True)
    tags = models.JSONField(default=list, null=True, blank=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="videos")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Video: {self.file_name} - Upload Date: {self.upload_date} - File Size: {self.file_size}"
