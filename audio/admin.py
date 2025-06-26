from django.contrib import admin
from audio.models import Audio


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'file_size', 'mime_type', 'duration', 'bitrate', 'sample_rate', 'channels', 'tags', 'genre', 'updated_at',)
    search_fields = ('tags', 'genre', 'file_name', 'mime_type', 'bitrate', 'channels', 'sample_rate',)
