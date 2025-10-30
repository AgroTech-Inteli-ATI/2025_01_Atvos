import os
import json
import uuid
from google.cloud import bigquery

class BigQueryClient:
    def __init__(self):
        # Opção 1: ler do .env JSON
        key_json_str = os.getenv("BIGQUERY_KEY_JSON")
        if key_json_str:
            key_info = json.loads(key_json_str)
            self.client = bigquery.Client.from_service_account_info(key_info)
        else:
            # Opção 2: ler arquivo físico
            key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            self.client = bigquery.Client()

        # Defina seu dataset e tabela padrão
        self.dataset_id = "agro_dataset"

    def table_ref(self, table_id):
        return f"{self.client.project}.{self.dataset_id}.{table_id}"

    def inserir(self, row: dict, table_id):
        """Insere um registro na tabela com ID UUID automático"""
        if "id" not in row or not row["id"]:
            row["id"] = str(uuid.uuid4())

        errors = self.client.insert_rows_json(self.table_ref(table_id), [row])
        if errors:
            raise Exception(f"Erro ao inserir: {errors}")
        return {"status": "ok", "row": row}


    def atualizar(self, row_id: str, updates: dict, table_id):
        """Atualiza registros da tabela por um campo id"""
        set_expr = ", ".join([f"{k}='{v}'" for k, v in updates.items()])
        query = f"""
        UPDATE `{self.table_ref(table_id)}`
        SET {set_expr}
        WHERE id = '{row_id}'
        """
        query_job = self.client.query(query)
        query_job.result()  # espera a conclusão
        return {"status": "ok", "updated_id": row_id}

    def remover(self, row_id: str, table_id):
        """Remove registros da tabela por um campo id"""
        query = f"""
        DELETE FROM `{self.table_ref(table_id)}`
        WHERE id = '{row_id}'
        """
        query_job = self.client.query(query)
        query_job.result()
        return {"status": "ok", "deleted_id": row_id}
