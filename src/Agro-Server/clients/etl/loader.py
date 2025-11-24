import os
import logging
import tempfile
from clients import storage_client, bigquery_client

logger = logging.getLogger(__name__)

def upload_to_gcs_and_load_bq(df, prefix: str, table_name: str):
    """
    Salva um DataFrame como CSV, faz upload para o GCS e carrega no BigQuery.
    """
    # Usar um arquivo temporário para o CSV
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as tmpfile:
        df.to_csv(tmpfile.name, index=False)
        csv_path = tmpfile.name

    try:
        # Define o caminho de destino no GCS
        destination_blob = f"{prefix}/{os.path.basename(csv_path)}"

        # Faz o upload para o GCS
        gcs_uri = storage_client.upload_file(csv_path, destination_blob)
        logger.info(f"Arquivo CSV enviado para {gcs_uri}")

        # Carrega os dados no BigQuery
        bigquery_client.load_csv_from_gcs(gcs_uri, table_name)
        logger.info(f"Dados carregados na tabela {table_name} do BigQuery")

        return gcs_uri

    finally:
        # Limpa o arquivo temporário
        if os.path.exists(csv_path):
            os.remove(csv_path)