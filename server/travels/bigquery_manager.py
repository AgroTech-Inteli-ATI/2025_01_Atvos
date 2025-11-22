import os
import logging
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core import retry
from google.api_core.exceptions import GoogleAPIError, BadRequest
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BigQueryManager:
    """
    Gerenciador de operações no Google BigQuery
    """

    def __init__(self):
        credentials_path = os.getenv(
            'GOOGLE_APPLICATION_CREDENTIALS',
            '/home/inteli/2025_01_Atvos/server/credentials/key.json'
        )

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Arquivo de credenciais não encontrado: {credentials_path}\n"
                "Configure a variável GOOGLE_APPLICATION_CREDENTIALS no .env"
            )

        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )

        self.project_id = os.getenv('PROJECT_ID', 'agro-data-476422')
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'agro_dataset')

        self.client = bigquery.Client(
            credentials=self.credentials,
            project=self.project_id
        )

        logger.info(f"BigQuery conectado: {self.project_id}.{self.dataset_id}")

    def get_table_id(self, table_name: str) -> str:
        return f"{self.project_id}.{self.dataset_id}.{table_name}"

    def get_table_id_quoted(self, table_name: str) -> str:
        return f"`{self.project_id}.{self.dataset_id}.{table_name}`"

    @retry.Retry(predicate=retry.if_transient_error, deadline=60.0)
    def query(self, sql: str, parameters: Optional[List] = None) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Executando query: {sql[:200]}...")

            job_config = bigquery.QueryJobConfig()
            job_config.use_legacy_sql = False

            query_job = self.client.query(sql, job_config=job_config)
            results = query_job.result()

            rows = []
            for row in results:
                rows.append(dict(row.items()))

            logger.info(f"Query executou com sucesso: {len(rows)} linhas retornadas")
            return rows

        except BadRequest as e:
            logger.error(f"Erro de SQL: {e.message}")
            raise
        except GoogleAPIError as e:
            logger.error(f"Erro BigQuery API: {str(e)}")
            raise

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> bool:
        try:
            table_ref = self.client.dataset(self.dataset_id).table(table_name)
            table = self.client.get_table(table_ref)

            if not rows:
                logger.warning(f"Tentativa de inserir lista vazia em {table_name}")
                return True

            schema_fields = {field.name for field in table.schema}
            cleaned_rows = []

            for row in rows:
                cleaned_row = {k: v for k, v in row.items() if k in schema_fields}
                cleaned_rows.append(cleaned_row)

            errors = self.client.insert_rows_json(table, cleaned_rows)

            if errors:
                logger.error(f"Erro ao inserir em {table_name}: {errors}")
                return False

            logger.info(f"{len(cleaned_rows)} linhas inseridas em {table_name}")
            return True

        except GoogleAPIError as e:
            logger.error(f"Erro BigQuery ao inserir em {table_name}: {str(e)}")
            return False

    def update_row(self, table_name: str, data: Dict[str, Any], where_clause: str) -> bool:
        """Atualiza linha(s) via UPDATE"""
        try:
            set_clauses = []
            for key, value in data.items():
                if key == 'id':
                    continue

                if isinstance(value, str):
                    value_escaped = value.replace("'", "''")
                    set_clauses.append(f"{key} = '{value_escaped}'")
                elif value is None:
                    set_clauses.append(f"{key} = NULL")
                elif isinstance(value, (int, float)):
                    set_clauses.append(f"{key} = {value}")
                else:
                    set_clauses.append(f"{key} = '{str(value)}'")

            if not set_clauses:
                logger.warning("Update sem campos para atualizar")
                return True

            table_id = self.get_table_id(table_name)

            sql = f"""
            UPDATE `{table_id}`
            SET {', '.join(set_clauses)}
            WHERE {where_clause}
            """

            logger.warning(f"Executando UPDATE: {sql[:200]}")
            query_job = self.client.query(sql)
            query_job.result()

            logger.info(f"UPDATE executado em {table_name}")
            return True

        except GoogleAPIError as e:
            logger.error(f"Erro ao atualizar {table_name}: {str(e)}")
            return False

    def update_or_insert(self, table_name, key_field, key_value, data):
        table_id = f"{self.client.project}.{self.dataset_id}.{table_name}"

        check_sql = f"""
            SELECT datetime
            FROM `{table_id}`
            WHERE {key_field} = @key_value
            ORDER BY datetime DESC
            LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("key_value", "STRING", key_value),
            ]
        )

        existing_rows = list(self.client.query(check_sql, job_config=job_config).result())

        if existing_rows:
            raise ValueError(f"Registro com {key_field}='{key_value}' já existe e não pode ser atualizado.")

        self.insert_row(table_name, data)
        return "inserted"


    def delete_rows(self, table_name: str, where_clause: str) -> bool:
        """Remove linhas via DELETE"""
        try:
            table_id = self.get_table_id(table_name)

            sql = f"""
            DELETE FROM `{table_id}`
            WHERE {where_clause}
            """

            logger.warning(f"Executando DELETE: {sql[:200]}")
            query_job = self.client.query(sql)
            query_job.result()

            logger.info(f"DELETE executado em {table_name}")
            return True

        except GoogleAPIError as e:
            logger.error(f"Erro ao deletar de {table_name}: {str(e)}")
            return False

    def execute_dml(self, sql: str) -> int:
        """Executa um DML raw"""
        try:
            query_job = self.client.query(sql)
            result = query_job.result()

            rows_affected = query_job.num_dml_affected_rows or 0
            logger.info(f"DML executado: {rows_affected} linhas afetadas")

            return rows_affected

        except GoogleAPIError as e:
            logger.error(f"Erro ao executar DML: {str(e)}")
            return 0
