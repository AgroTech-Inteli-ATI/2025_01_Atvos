# api/urls.py
from django.urls import path
from . import bigquery_views
from . import storage_views
from .bigquery_views import criar_view_diaria, criar_view_mensal, exportar_view

urlpatterns = [
    path("api/bigquery/inserir/", bigquery_views.inserir_registro),
    path("api/bigquery/atualizar/", bigquery_views.atualizar_registro),
    path("api/bigquery/remover/", bigquery_views.remover_registro),

    # Cloud Storage
    path("api/storage/upload/", storage_views.upload_arquivo),
    path("api/storage/remover/", storage_views.remover_arquivo),
    path("api/storage/download/", storage_views.download_arquivo),

    path('bigquery/view/diaria', criar_view_diaria, name='criar_view_diaria'),
    path('bigquery/view/mensal', criar_view_mensal, name='criar_view_mensal'),
    path('bigquery/view/exportar', exportar_view, name='exportar_view'),
 
]
