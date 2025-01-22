from django.contrib import admin
from video.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'file_size', 'mime_type', 'resolution', 'frame_rate', 'video_codec', 'audio_codec', 'bitrate', 'tags', 'genre')
    search_fields = ('tags', 'genre', 'file_size', 'mime_type', 'resolution', 'frame_rate', 'video_codec', 'audio_codec', 'bitrate', 'file_name')
