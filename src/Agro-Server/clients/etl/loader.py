import os
import logging
from clients import storage_client, bigquery_client

logger = logging.getLogger(__name__)

def load_data(df, bucket_name, table_name):
    # Salvar CSV localmente
    csv_path = '/tmp/viagens.csv'
    df.to_csv(csv_path, index=False)
    storage_client.upload_file_to_bucket(csv_path, bucket_name, 'viagens.csv')
    bigquery_client.load_csv_from_gcs(f'gs://{bucket_name}/viagens.csv', 'your_dataset', table_name)
    logger.info("Data loaded to BigQuery table %s", table_name)