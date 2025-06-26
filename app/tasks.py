import ffmpeg
import io
import json
import os
import subprocess
import uuid
from celery import shared_task, chord
from video.models import Video


@shared_task(queue='metadata_extract_processing_queue')
def extract_video_info_task(video_path):
    try:
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"O arquivo {video_path} não foi encontrado.")

        
        # Comando para obter informações do vídeo usando ffprobe
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        output = subprocess.check_output(command).decode()
        probe = json.loads(output)

        # Obtendo informações do fluxo de vídeo
        video_stream = next(
            stream for stream in probe['streams'] if stream['codec_type'] == 'video'
        )
        audio_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
            None
        )

        # Cálculo de frame_rate
        frame_rate = video_stream['avg_frame_rate'].split('/')
        frame_rate = float(frame_rate[0]) / float(frame_rate[1]) if len(frame_rate) == 2 else float(frame_rate[0])

        
        # Extraindo informações conforme o modelo
        info = {
            "duration": float(probe['format'].get('duration', 0.0)),
            "resolution": f"{video_stream['width']}x{video_stream['height']}",
            "frame_rate": frame_rate,  # Convertendo string para float
            "video_codec": video_stream.get('codec_name', None),
            "audio_codec": audio_stream.get('codec_name', None) if audio_stream else None,
            "bitrate": int(probe['format'].get('bit_rate', 0)) // 1000  # Convertendo para kbps
        }

        return info

    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(f"Erro ao processar o vídeo: {video_path} - {e}")

@shared_task(queue='thumbnail_generation_queue')
def generate_video_thumbnail_task(file_path):
    try:
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
        
        output_buffer = io.BytesIO()
        output_file = os.path.join(os.path.dirname(file_path).replace('original', 'thumbnails'), f"{uuid.uuid4().hex}_thumbnail.jpg")
        
        # Usar o FFmpeg para gerar a thumbnail
        ffmpeg.input(file_path, ss=1).output(output_file, vframes=1).run()

        # Ler a imagem gerada
        with open(output_file, 'rb') as img_file:
            output_buffer.write(img_file.read())
        
        output_buffer.seek(0)

        return output_file

    except Exception as e:
        raise Exception(f'Erro gerando capa do vídeo: {e}')

@shared_task(queue='video_resolution_process_queue')
def process_video_qualities_task(file_path):
    
    if not os.path.exists(file_path):
            raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
    
    resolutions = {
        "1080p": "1920x1080",
        "720p": "1280x720",
        "480p": "854x480"
    }
    output_paths = {}
    
    processed_folder = os.path.dirname(file_path).replace('original', 'processed')

    try:

        for label, resolution in resolutions.items():
            original_name = os.path.splitext(os.path.basename(file_path))[0]
            
            output_file = os.path.join(processed_folder, f"{original_name.rsplit('.', 1)[0]}_{label}.mp4")
            ffmpeg.input(file_path).output(output_file, vf=f"scale={resolution}", preset="fast", vb="1M").run()
            output_paths[label] = output_file

        return output_paths

    except Exception as e:
        raise Exception(f'Erro ao processar qualidades de vídeo: {e}')

@shared_task(queue='finalize_video_process')
def finalize_processing(results, video_id=None):
    try:

        metadata, vid_thumbnail, vid_resolutions = results
        
        video = Video.objects.filter(id=video_id).first()
        if not video:
            raise ValueError(f'Vídeo de Id {video_id} não encontrado.')
        
        video.status = Video.COMPLETED
        video.duration = metadata.get('duration')
        video.resolution = metadata.get('resolution')
        video.frame_rate = metadata.get('frame_rate')
        video.video_codec = metadata.get('video_codec')
        video.audio_codec = metadata.get('audio_codec')
        video.bitrate = metadata.get('bitrate')
        video.thumbnail_path = vid_thumbnail
        video.processing_details = vid_resolutions
        
        video.save()
    except Exception as e:
        raise Exception(f'Erro ao finalizar o processamento do vídeo: {e}')

def process_upload_video(video_id, file_path):
    
    chord(
        [
            extract_video_info_task.s(file_path),
            generate_video_thumbnail_task.s(file_path),
            process_video_qualities_task.s(file_path)
        ]
    )(finalize_processing.s(video_id=video_id))
    
