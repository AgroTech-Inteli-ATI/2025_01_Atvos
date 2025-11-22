"""Camada de serviço responsável pelo fluxo ETL dos arquivos brutos.

O objetivo é receber o nome de um blob armazenado no Google Cloud Storage, realizar
as etapas de extração, transformação e carga (ETL) e devolver um resumo do
processamento executado. A implementação foi pensada para ser simples, mas
expressiva o suficiente para atender ao pipeline descrito na documentação do
projeto.
"""
from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional

import pandas as pd

from clients.bigquery_client import BigQueryClient
from clients.storage_client import CloudStorageClient


@dataclass(slots=True)
class EtlResult:
    """Representa o resultado consolidado de uma execução do ETL."""

    status: str
    message: str
    raw_blob: str
    staging_blob: Optional[str]
    table: Optional[str]
    rows_read: int
    rows_loaded: int
    processed_at: str

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "mensagem": self.message,
            "raw_blob": self.raw_blob,
            "staging_blob": self.staging_blob,
            "table": self.table,
            "rows_read": self.rows_read,
            "rows_loaded": self.rows_loaded,
            "processed_at": self.processed_at,
        }


class EtlService:
    """Serviço de ETL que consome arquivos CSV no bucket *raw* e carrega no BigQuery.

    Fluxo básico:
    1. Baixa o arquivo indicado pelo *blob* no bucket configurado.
    2. Aplica transformações simples (drop de duplicados, normalização de nomes de
       colunas e remoção de linhas vazias).
    3. Carrega os dados tratados para uma tabela do BigQuery.
    4. Persiste uma cópia tratada no bucket na camada *staging*.
    """

    DEFAULT_TARGET_TABLE = "raw_layer"
    DEFAULT_STAGING_PREFIX = "staging/"
    DEFAULT_RAW_PREFIX = "raw/"
    DEFAULT_CHUNK_SIZE = 500

    def __init__(
        self,
        storage_client: Optional[CloudStorageClient] = None,
        bigquery_client: Optional[BigQueryClient] = None,
        *,
        chunk_size: Optional[int] = None,
    ) -> None:
        self.storage_client = storage_client or CloudStorageClient()
        self.bigquery_client = bigquery_client or BigQueryClient()
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.target_table = os.getenv("BIGQUERY_ETL_TABLE", self.DEFAULT_TARGET_TABLE)
        self.raw_prefix = os.getenv("RAW_LAYER_PREFIX", self.DEFAULT_RAW_PREFIX)
        self.staging_prefix = os.getenv("STAGING_LAYER_PREFIX", self.DEFAULT_STAGING_PREFIX)

    # ==============================
    # API pública
    # ==============================
    def process_raw_file(self, blob_name: str) -> dict:
        """Executa o pipeline ETL para um blob do bucket Cloud Storage."""
        if not blob_name:
            raise ValueError("O parâmetro 'blob_name' é obrigatório.")

        normalized_blob = blob_name.strip()
        if not normalized_blob.lower().endswith(".csv"):
            raise ValueError("Apenas arquivos no formato CSV são suportados nesta versão.")

        raw_bytes = self.storage_client.download_buffer(normalized_blob)
        dataframe = self._read_csv(raw_bytes)
        rows_read = len(dataframe)

        if dataframe.empty:
            result = self._build_result(
                status="ok",
                message="Arquivo processado, mas não foram encontrados registros.",
                raw_blob=normalized_blob,
                staging_blob=None,
                table=None,
                rows_read=0,
                rows_loaded=0,
            )
            return result.as_dict()

        dataframe = self._transform_dataframe(dataframe)
        records = self._prepare_records(dataframe)

        rows_loaded = self._load_to_bigquery(records)
        staging_blob = self._persist_staging_artifact(dataframe, normalized_blob)

        result = self._build_result(
            status="ok",
            message="Processamento concluído com sucesso.",
            raw_blob=normalized_blob,
            staging_blob=staging_blob,
            table=self.bigquery_client.table_ref(self.target_table) if rows_loaded else None,
            rows_read=rows_read,
            rows_loaded=rows_loaded,
        )
        return result.as_dict()

    # ==============================
    # Etapas do pipeline
    # ==============================
    def _read_csv(self, file_bytes: bytes) -> pd.DataFrame:
        """Converte os bytes do arquivo CSV em um DataFrame pandas."""
        try:
            return pd.read_csv(io.BytesIO(file_bytes))
        except UnicodeDecodeError:
            # fallback para arquivos com acentuação em latin-1
            return pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

    def _transform_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Aplica transformações básicas no DataFrame."""
        dataframe = dataframe.dropna(how="all")
        dataframe = dataframe.drop_duplicates()
        dataframe.columns = [self._normalize_column(col) for col in dataframe.columns]
        return dataframe

    def _prepare_records(self, dataframe: pd.DataFrame) -> List[dict]:
        """Prepara os registros para inserção no BigQuery."""
        prepared = []
        for row in dataframe.to_dict(orient="records"):
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned_row[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    cleaned_row[key] = value.isoformat()
                else:
                    cleaned_row[key] = value
            prepared.append(cleaned_row)
        return prepared

    def _load_to_bigquery(self, records: List[dict]) -> int:
        """Insere os registros em uma tabela do BigQuery."""
        if not records:
            return 0

        table_ref = self.bigquery_client.table_ref(self.target_table)
        total_inserted = 0
        errors: List[dict] = []

        for chunk in self._chunk(records, self.chunk_size):
            response = self.bigquery_client.client.insert_rows_json(table_ref, chunk)
            if response:
                errors.extend(response)
            else:
                total_inserted += len(chunk)

        if errors:
            raise RuntimeError(f"Falha ao inserir registros no BigQuery: {errors}")

        return total_inserted

    def _persist_staging_artifact(self, dataframe: pd.DataFrame, raw_blob: str) -> str:
        """Gera um artefato tratado e envia para a camada *staging* no bucket."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base_name = os.path.basename(raw_blob)
        sanitized_name = os.path.splitext(base_name)[0]
        staging_blob_name = f"{self.staging_prefix}{sanitized_name}_processed_{timestamp}.csv"

        buffer = io.BytesIO()
        dataframe.to_csv(buffer, index=False)
        staging_bytes = buffer.getvalue()
        self.storage_client.upload_buffer(staging_bytes, staging_blob_name)
        return staging_blob_name

    # ==============================
    # Utilidades
    # ==============================
    def _build_result(
        self,
        *,
        status: str,
        message: str,
        raw_blob: str,
        staging_blob: Optional[str],
        table: Optional[str],
        rows_read: int,
        rows_loaded: int,
    ) -> EtlResult:
        processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return EtlResult(
            status=status,
            message=message,
            raw_blob=raw_blob,
            staging_blob=staging_blob,
            table=table,
            rows_read=rows_read,
            rows_loaded=rows_loaded,
            processed_at=processed_at,
        )

    def _normalize_column(self, column_name: str) -> str:
        """Normaliza nomes de colunas (snake_case) para consistência."""
        normalized = re.sub(r"[^0-9a-zA-Z]+", "_", column_name.strip().lower())
        return normalized.strip("_")

    def _chunk(self, iterable: Iterable[dict], size: int) -> Iterable[List[dict]]:
        """Agrupa os itens do iterável em blocos de `size` itens."""
        chunk: List[dict] = []
        for item in iterable:
            chunk.append(item)
            if len(chunk) == size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk