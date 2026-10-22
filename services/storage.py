from io import BufferedReader
from pathlib import Path
from minio import Minio

class StorageService: 
    def __init__(
        self, 
        endpoint: str, 
        access_key: str, 
        secret_key: str, 
        bucket_name: str, 
        secure: bool = False, 
    ) -> None:
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = bucket_name
        self._ensure_bucket()
        
    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            
    def upload(
        self, 
        object_name: str, 
        file_data: BufferedReader, 
        length: int, 
        content_type: str
    ) -> None:
        self.client.put_object(
            self.bucket_name,
            object_name,
            file_data,
            length,
            content_type=content_type,
        )
        
    def download(self, object_name: str):
        return self.client.get_object(self.bucket_name, object_name)

    def download_to_file(
        self,
        object_name: str,
        destination: Path,
    ) -> None:
        response = self.client.get_object(
            self.bucket_name,
            object_name,
        )
        try:
            with destination.open("wb") as output:
                for chunk in response.stream(amt=1024 * 1024, decode_content=True):
                    if chunk:
                        output.write(chunk)
        finally:
            response.close()
            response.release_conn()
