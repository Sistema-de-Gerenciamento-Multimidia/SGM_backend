import os
import uuid
from urllib.parse import urlparse


def generate_s3_url(user_id: int, filename: str, is_thumbnail=False, thumbnail_unique_name='', is_audio=False):
    """
    Gera o link público para o vídeo ou thumbnail armazenado no S3.
    
    :param user_id: ID do usuário (usado para organizar os arquivos no S3).
    :param filename: Nome do arquivo de vídeo (sem caminho completo).
    :param is_thumbnail: Se for True, gera o link para a thumbnail, senão para o vídeo.
    :return: URL pública no S3.
    """
    bucket_name = os.environ.get('AWS_BUCKET_NAME')
    
    if is_thumbnail:
        s3_path = f'user/{user_id}/videos/{thumbnail_unique_name}'
    elif is_audio:
        s3_path = f'user/{user_id}/audios/{filename}'
    else:
        s3_path = f'user/{user_id}/videos/{filename}'
    
    s3_url = f"https://{bucket_name}.s3.{os.environ.get('AWS_REGION')}.amazonaws.com/{s3_path}"
    
    return s3_url

def extract_s3_key(s3_url):
    parsed_url = urlparse(s3_url)
    return parsed_url.path.lstrip('/') # Remove a barra inicial do caminho
