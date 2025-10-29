from django.urls import path
from api import bigquery_views

urlpatterns = [
    path("api/inserir/", bigquery_views.inserir_registro),
    path("api/atualizar/", bigquery_views.atualizar_registro),
    path("api/remover/", bigquery_views.remover_registro),
]
