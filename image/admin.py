from django.contrib import admin
from image.models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'file_size', 'mime_type', 'dimensions', 'color_depth', 'resolution', 'updated_at',)
    search_fields = ('tags', 'file_name', 'mime_type', 'dimensions',)
