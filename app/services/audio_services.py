import ffmpeg
import os
import subprocess
import json
import soundfile as sf


import subprocess
import json
import soundfile as sf


def extract_audio_info(audio_path):
    try:
        # Use ffprobe for metadata extraction
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", audio_path
        ]
        output = subprocess.check_output(command).decode()
        probe_data = json.loads(output)

        # Extract duration and bitrate from ffprobe data
        format_info = probe_data.get('format', {})
        duration = float(format_info.get('duration', 0))
        bitrate = int(format_info.get('bit_rate', 0)) // 1000  # Convert to kbps

        # Extract sample rate and channels using soundfile
        info = sf.info(audio_path)
        sample_rate = info.samplerate
        channels = info.channels

        # Return extracted audio properties
        audio_data = {
            "duration": duration,
            "bitrate": bitrate,
            "sample_rate": sample_rate,
            "channels": channels
        }

        return audio_data

    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(f"Error processing audio: {audio_path} - {e}")
        
def save_video_in_temporary_file(video, video_path):
    with open(video_path, 'wb+') as destination:
        for chunk in video.chunks():
            destination.write(chunk)

def remove_video_in_temporary_file(video_path):
    if os.path.exists(video_path):
        os.remove(video_path)

