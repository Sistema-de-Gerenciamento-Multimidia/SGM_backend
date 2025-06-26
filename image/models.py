from django.db import models
from users.models import CustomUser


class Image(models.Model):
    file_name = models.CharField(max_length=255, null=False, blank=False)
    file_hash = models.CharField(max_length=255, unique=True, null=False, blank=False) # Nome único do arquivo salvo no servidor para controle de duplicações
    file_size = models.BigIntegerField() # In bytes
    upload_date = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255, null=False, blank=False, unique=True)
    
    dimensions = models.CharField(max_length=255, null=True, blank=True) # Ex: width x height
    color_depth = models.CharField(max_length=255, null=True, blank=True)
    resolution = models.CharField(max_length=255, null=True, blank=True) # Ex: dpi_x x dpi_y
    exif_metadata = models.JSONField(default=dict, null=True, blank=True)
    # Exemplo de Estrutura:
    # {
    #     "CameraModel": "Canon EOS 5D Mark IV",
    #     "CaptureDatetime": "2024-02-25 14:30:00",
    #     "GPSLatitude": -23.5505,
    #     "GPSLongitude": -46.6333,
    #     "etc..."
    # }
    
    description = models.TextField(null=True, blank=True)
    tags = models.JSONField(default=list, null=True, blank=True)
    
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="images")

    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Image: {self.file_name} - Upload Date: {self.upload_date} - File Size: {self.file_size}"
