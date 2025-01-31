# Generated by Django 5.1.3 on 2025-01-20 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('file_size', models.BigIntegerField()),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('mime_type', models.CharField(max_length=255)),
                ('duration', models.FloatField()),
                ('resolution', models.CharField(max_length=255)),
                ('frame_rate', models.FloatField()),
                ('video_codec', models.CharField(max_length=255)),
                ('audio_codec', models.CharField(max_length=255)),
                ('bitrate', models.IntegerField()),
                ('thumbnail_path', models.CharField(max_length=255)),
                ('processing_details', models.JSONField(default=dict)),
                ('description', models.TextField(blank=True, null=True)),
                ('tags', models.JSONField(default=list)),
                ('genre', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
