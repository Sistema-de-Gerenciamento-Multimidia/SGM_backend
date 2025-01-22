from django.db import models
from users.models import CustomUser


class Image(models.Model):
    file_name = models.CharField(max_length=255, null=False, blank=False)
    file_size = models.BigIntegerField() # In bytes
    upload_date = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255, null=False, blank=False, unique=True)
    
    description = models.TextField(null=True, blank=True)
    tags = models.JSONField(default=list, null=True, blank=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="images")
    
    def __str__(self):
        return f"Image: {self.file_name} - Upload Date: {self.upload_date} - File Size: {self.file_size}"
