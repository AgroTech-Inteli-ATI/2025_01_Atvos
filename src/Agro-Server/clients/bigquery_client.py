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
        self.dataset_id = os.getenv("BIGQUERY_DATASET_NAME", "agro_dataset")

    def load_csv_from_gcs(self, gcs_uri: str, table_id: str):
        """Carrega um CSV do GCS para uma tabela do BigQuery."""
        table_ref = self.client.dataset(self.dataset_id).table(table_id)

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        load_job = self.client.load_table_from_uri(
            gcs_uri, table_ref, job_config=job_config
        )
        load_job.result()  # Espera a conclusão do job

        if load_job.errors:
            raise Exception(f"Erro no job de carga do BigQuery: {load_job.errors}")

        return f"Dados carregados com sucesso em {self.dataset_id}.{table_id}"


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
        set_parts = []
        for k, v in updates.items():
            if isinstance(v, (int, float)):
                set_parts.append(f"{k} = {v}")
            elif isinstance(v, bool):
                set_parts.append(f"{k} = {str(v).upper()}")
            elif v is None:
                set_parts.append(f"{k} = NULL")
            else:
                # Escapa aspas simples em strings
                v_escaped = str(v).replace("'", "\\'")
                set_parts.append(f"{k} = '{v_escaped}'")
        
        set_expr = ", ".join(set_parts)
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

    def listar(self, table_id, limit=None, offset=0, order_by="id"):
        """Lista todos os registros da tabela"""
        query = f"SELECT * FROM `{self.table_ref(table_id)}`"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if offset and offset > 0:
            query += f" OFFSET {offset}"

        query_job = self.client.query(query)
        results = query_job.result()
        
        rows = []
        for row in results:
            row_dict = dict(row)
            rows.append(row_dict)
        
        return rows

    def buscar_por_id(self, table_id, row_id):
        """Busca um registro por ID"""
        query = f"""
        SELECT * FROM `{self.table_ref(table_id)}`
        WHERE id = '{row_id}'
        LIMIT 1
        """
        query_job = self.client.query(query)
        results = list(query_job.result())
        
        if not results:
            return None
        
        return dict(results[0])

    def filtrar(self, table_id, filters: dict, limit=None, offset=0, order_by="id"):
        """Filtra registros por condições (ex: {"unit_id": "1"})"""
        query = f"SELECT * FROM `{self.table_ref(table_id)}`"
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                else:
                    conditions.append(f"{key} = {value}")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if offset and offset > 0:
            query += f" OFFSET {offset}"

        query_job = self.client.query(query)
        results = query_job.result()
        
        rows = []
        for row in results:
            row_dict = dict(row)
            rows.append(row_dict)
        
        return rows

    def executar_query(self, query: str):
        """Executa uma query SQL customizada e retorna os resultados"""
        query_job = self.client.query(query)
        results = query_job.result()
        
        rows = []
        for row in results:
            row_dict = dict(row)
            rows.append(row_dict)
        
        return rows
   

    def execute_query(self, query):
        """Executa uma query SQL no BigQuery"""
        query = query.format(
            project=self.project,
            dataset=self.dataset
        )
        return self.client.query(query)

    def query_to_dataframe(self, query):
        """Executa uma query e retorna os resultados como DataFrame"""
        return self.client.query(query).to_dataframe()
