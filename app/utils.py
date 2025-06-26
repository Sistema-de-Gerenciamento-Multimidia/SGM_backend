import os
import hashlib
from audio.models import Audio
from image.models import Image
from video.models import Video


def generate_sha256_file_hash(file, user):
    """Gera um hash único para cada arquivo a partir do seu conteúdo e do usuário"""
    sha256 = hashlib.sha256()
    file.seek(0)
    while True:
        chunk = file.read(4096)
        if not chunk:
            break
        sha256.update(chunk)
    file.seek(0)
    
    sha256.update(str(user.id).encode('utf-8'))
    
    return sha256.hexdigest()
        

def is_file_duplicated(file_hash, file_type: str, user):
    """
    Verifica se o arquivo já existe no banco de dados através do hash(feito baseado no conteúdo do arquivo).
    file_type devem ser do tipo "Image, Video ou Audio"
    """
    if file_type == "Audio":
        return Audio.objects.filter(file_hash=file_hash, user=user).exists()
    elif file_type == "Image":
        return Image.objects.filter(file_hash=file_hash, user=user).exists()
    elif file_type == "Video":
        return Video.objects.filter(file_hash=file_hash, user=user).exists()
    else:
        raise ValueError("Tipo de arquivo inválido. O arquivo deve ser do tipo 'Audio', 'Image' ou 'Video'.")
    

def save_image(image, image_path):
    with open(image_path, 'wb+') as destination:
        destination.write(image.read())

def save_media(file, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def remove_media(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
