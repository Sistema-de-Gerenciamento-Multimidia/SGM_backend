from django.db import models
from users.models import CustomUser


class Audio(models.Model):
    file_name = models.CharField(max_length=255, null=False, blank=False)
    file_size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255, null=False, blank=False, unique=True)
    
    # Propriedades específicas do áudio
    duration = models.FloatField(null=True, blank=True)  # Duração em segundos
    bitrate = models.PositiveIntegerField(null=True, blank=True)  # Taxa de bits em kbps
    sample_rate = models.PositiveIntegerField(null=True, blank=True)  # Taxa de amostragem em Hz
    channels = models.PositiveSmallIntegerField(null=True, blank=True)  # Número de canais

    # Propriedades definidas pelo usuário
    description = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)  # Lista de tags como JSON
    genre = models.CharField(max_length=100, null=True, blank=True)
    
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="audios")
    
    def __str__(self):
        return f"Audio: {self.file_name} - Upload Date: {self.upload_date} - File Size: {self.file_size}"
