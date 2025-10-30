# api/storage_client.py
import io
import os
from google.cloud import storage
from api import settings


class CloudStorageClient:
    """Cliente do Google Cloud Storage com suporte a buffers em memória."""

    def __init__(self):
        key_json_str = os.getenv("BIGQUERY_KEY_JSON")
        if key_json_str:
            key_info = json.loads(key_json_str)
            self.client = storage.Client.from_service_account_info(key_info)
        else:
            # Opção 2: ler arquivo físico
            key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            self.client = storage.Client()
        self.bucket_name = os.getenv("CLOUD_STORAGE_BUCKET")
        if not self.bucket_name:
            raise ValueError("A variável CLOUD_STORAGE_BUCKET não está definida no .env")
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_buffer(self, file_bytes: bytes, destination_blob: str):
        """
        Faz upload de um arquivo recebido como bytes (buffer) para o bucket.
        :param file_bytes: Conteúdo do arquivo em bytes
        :param destination_blob: Caminho destino no bucket (ex: 'uploads/imagem.jpg')
        """
        blob = self.bucket.blob(destination_blob)
        blob.upload_from_file(io.BytesIO(file_bytes), rewind=True)
        return {"mensagem": f"Arquivo enviado com sucesso para '{destination_blob}' no bucket '{self.bucket_name}'."}

    def delete_file(self, blob_name: str):
        """
        Remove um arquivo do bucket.
        :param blob_name: Caminho do arquivo no bucket
        """
        blob = self.bucket.blob(blob_name)
        if not blob.exists():
            return {"erro": f"O arquivo '{blob_name}' não existe no bucket '{self.bucket_name}'."}
        blob.delete()
        return {"mensagem": f"Arquivo '{blob_name}' removido com sucesso do bucket '{self.bucket_name}'."}

    def download_buffer(self, blob_name: str) -> bytes:
        """
        Baixa um arquivo do bucket e retorna o conteúdo como bytes.
        :param blob_name: Caminho do arquivo no bucket
        :return: Conteúdo em bytes
        """
        blob = self.bucket.blob(blob_name)
        if not blob.exists():
            raise FileNotFoundError(f"O arquivo '{blob_name}' não existe no bucket '{self.bucket_name}'.")

        buffer = io.BytesIO()
        blob.download_to_file(buffer)
        buffer.seek(0)  # volta o ponteiro ao início
        return buffer.read()
