import os
import unittest
from typing import List, cast

from api.etl_service import EtlService
from clients.bigquery_client import BigQueryClient
from clients.storage_client import CloudStorageClient


class MockStorageClient:
    def __init__(self, csv_payload: str):
        self._payload = csv_payload.encode("utf-8")
        self.upload_calls: List[tuple[str, bytes]] = []

    def download_buffer(self, blob_name: str) -> bytes:
        return self._payload

    def upload_buffer(self, file_bytes: bytes, destination_blob: str) -> dict:
        self.upload_calls.append((destination_blob, file_bytes))
        return {"mensagem": "ok"}


class MockBigQueryClient:
    def __init__(self):
        self.insert_calls: List[List[dict]] = []
        self.table_ids: List[str] = []
        self.client = self

    def table_ref(self, table_id: str) -> str:
        ref = f"mock-project.dataset.{table_id}"
        self.table_ids.append(ref)
        return ref

    def insert_rows_json(self, table_ref: str, rows: List[dict]):
        self.insert_calls.append(rows)
        return []


class EtlServiceTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("BIGQUERY_ETL_TABLE", None)
        os.environ.pop("RAW_LAYER_PREFIX", None)
        os.environ.pop("STAGING_LAYER_PREFIX", None)

    def test_successful_processing_chunks_and_staging(self):
        csv_payload = "id_col,name,valor\n1,Ana,10\n2,Bia,20\n2,Bia,20\n"
        storage = MockStorageClient(csv_payload)
        bigquery = MockBigQueryClient()

        service = EtlService(
            storage_client=cast(CloudStorageClient, storage),
            bigquery_client=cast(BigQueryClient, bigquery),
            chunk_size=2,
        )
        result = service.process_raw_file("raw/sample.csv")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["rows_read"], 3)
        self.assertEqual(result["rows_loaded"], 2)
        self.assertTrue(result["processed_at"].endswith("Z"))
        self.assertEqual(result["raw_blob"], "raw/sample.csv")
        self.assertIsNotNone(result["staging_blob"])
        self.assertTrue(result["staging_blob"].startswith("staging/"))

        self.assertEqual(len(storage.upload_calls), 1)
        staging_blob, staging_bytes = storage.upload_calls[0]
        self.assertEqual(staging_blob, result["staging_blob"])
        self.assertIn("id_col", staging_bytes.decode("utf-8"))

        self.assertEqual(len(bigquery.insert_calls), 1)
        self.assertEqual(len(bigquery.insert_calls[0]), 2)
        self.assertRegex(result["table"], r"mock-project\.dataset\.raw_layer")

    def test_rejects_non_csv_file(self):
        storage = MockStorageClient("col1,col2\n1,2\n")
        bigquery = MockBigQueryClient()
        service = EtlService(
            storage_client=cast(CloudStorageClient, storage),
            bigquery_client=cast(BigQueryClient, bigquery),
        )

        with self.assertRaises(ValueError):
            service.process_raw_file("raw/data.txt")

    def test_empty_dataset_returns_zero_load(self):
        storage = MockStorageClient("col1,col2\n")
        bigquery = MockBigQueryClient()
        service = EtlService(
            storage_client=cast(CloudStorageClient, storage),
            bigquery_client=cast(BigQueryClient, bigquery),
        )

        result = service.process_raw_file("raw/empty.csv")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["rows_read"], 0)
        self.assertEqual(result["rows_loaded"], 0)
        self.assertIsNone(result["staging_blob"])
        self.assertIsNone(result["table"])
        self.assertEqual(len(bigquery.insert_calls), 0)
        self.assertEqual(len(storage.upload_calls), 0)


if __name__ == "__main__":
    unittest.main()
