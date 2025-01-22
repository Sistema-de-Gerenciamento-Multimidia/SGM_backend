# Generated by Django 5.1.3 on 2025-01-20 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='file_path',
            field=models.CharField(default='/path', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='video',
            name='file_name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
