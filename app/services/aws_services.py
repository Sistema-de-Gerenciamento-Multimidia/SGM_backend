import boto3
import io
import os
import uuid
from app.utils.s3_utils import generate_s3_url


class AWSServices:

    def __init__(self):
        self.__aws_s3_client = self.get_aws_client('s3')
        
    def get_aws_client(self, tipo_client: str) -> boto3.client:
        """
        Criação de um cliente de acesso aos serviços do bucket
        """
        client = boto3.client(
            service_name=tipo_client,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
            region_name=os.environ.get('AWS_REGION')
        )
        
        return client
    
    def upload_video_to_s3(self, video_filename: str, video_path: str, user_id: int):
        
        file_unique_name = f"{uuid.uuid4().hex}_video_{video_filename}"
        
        s3_key = f'user/{user_id}/videos/{file_unique_name}'
        
        self.__aws_s3_client.upload_file(
            video_path,
            os.environ.get('AWS_BUCKET_NAME'),
            s3_key,
        )
        
        return generate_s3_url(user_id, file_unique_name, is_thumbnail=False)

    
    def upload_file_to_s3(self, video_filename: str, thumbnail: io.BytesIO, user_id: int):
        try:
            # Gera um nome único para a thumbnail usando UUID
            thumbnail_unique_name = f"{uuid.uuid4().hex}_thumbnail_{video_filename}.jpg"
            
            # Coloca a miniatura diretamente no S3
            thumbnail.seek(0)  # Garante que o buffer está no início
            s3_key = f'user/{user_id}/videos/{thumbnail_unique_name}'
            
            self.__aws_s3_client.upload_fileobj(
                thumbnail, 
                os.environ.get('AWS_BUCKET_NAME'), 
                s3_key  # Caminho para salvar a thumbnail
            )
            
            return generate_s3_url(user_id, video_filename, is_thumbnail=True, thumbnail_unique_name=thumbnail_unique_name)
                
        except Exception as e:
            raise Exception(f"Erro ao fazer upload da thumbnail para o S3: {str(e)}")
    
    def delete_object_from_s3(self, video_file_path):
        self.__aws_s3_client.delete_object(
            Bucket=os.environ.get('AWS_BUCKET_NAME'),
            Key=video_file_path
        )


aws_services = AWSServices()
