import ffmpeg
import io
import json
import os
import subprocess
import uuid


def extract_video_info(video_path):
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
        
def generate_video_thumbnail(file_path):
    try:
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
        
        output_buffer = io.BytesIO()
        output_file = os.path.join(os.path.dirname(file_path), f"{uuid.uuid4().hex}_thumbnail.jpg")
        
        # Usar o FFmpeg para gerar a thumbnail
        ffmpeg.input(file_path, ss=1).output(output_file, vframes=1).run()

        # Ler a imagem gerada
        with open(output_file, 'rb') as img_file:
            output_buffer.write(img_file.read())
        
        output_buffer.seek(0)
        os.remove(output_file)
        return output_buffer

    except Exception as e:
        raise Exception(f'Erro gerando capa do vídeo: {e}')

def process_video_qualities(file_path):
    resolutions = {
        "1080p": "1920x1080",
        "720p": "1280x720",
        "480p": "854x480"
    }
    output_paths = {}

    try:

        for label, resolution in resolutions.items():
            output_file = f"{file_path.rsplit('.', 1)[0]}_{label}.mp4"
            ffmpeg.input(file_path).output(output_file, vf=f"scale={resolution}", preset="fast", vb="1M").run()
            output_paths[label] = output_file

        return output_paths

    except Exception as e:
        raise Exception(f'Erro ao processar qualidades de vídeo: {e}')

def save_video_in_temporary_file(video, video_path):
    with open(video_path, 'wb+') as destination:
        for chunk in video.chunks():
            destination.write(chunk)

def remove_video_in_temporary_file(video_path):
    if os.path.exists(video_path):
        os.remove(video_path)
