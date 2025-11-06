# api/urls.py
from django.urls import path
from . import bigquery_views
from . import storage_views

urlpatterns = [
    path("api/bigquery/inserir/", bigquery_views.inserir_registro),
    path("api/bigquery/atualizar/", bigquery_views.atualizar_registro),
    path("api/bigquery/remover/", bigquery_views.remover_registro),

    # Cloud Storage
    path("api/storage/upload/", storage_views.upload_arquivo),
    path("api/storage/remover/", storage_views.remover_arquivo),
    path("api/storage/download/", storage_views.download_arquivo)
]
