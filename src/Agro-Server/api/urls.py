# api/urls.py
from django.urls import path
from . import bigquery_views
from . import storage_views
from . import units_views
from . import occurrences_views
from . import travels_views
from . import dashboard_views
from .bigquery_views import criar_view_diaria, criar_view_mensal, exportar_view


urlpatterns = [
    # BigQuery genérico
    path("api/bigquery/inserir/", bigquery_views.inserir_registro),
    path("api/bigquery/atualizar/", bigquery_views.atualizar_registro),
    path("api/bigquery/remover/", bigquery_views.remover_registro),

    # Cloud Storage
    path("api/storage/upload/", storage_views.upload_arquivo),
    path("api/storage/remover/", storage_views.remover_arquivo),
    path("api/storage/download/", storage_views.download_arquivo),
    
    # Módulo: Unidades
    path("api/units/<str:unit_id>/stats/", units_views.stats_unit, name="stats_unit"),
    path("api/units/<str:unit_id>/", units_views.unidade_detail_view, name="unidade_detail"),  # GET, PUT, DELETE
    path("api/units/", units_views.unidades_view, name="unidades"),  # GET (listar), POST (criar)
    
    # Módulo: Ocorrências
    path("api/occurrences/categories/", occurrences_views.listar_categories, name="listar_categories"),
    path("api/occurrences/stats/", occurrences_views.stats_occurrences, name="stats_occurrences"),
    path("api/occurrences/<str:occurrence_id>/", occurrences_views.occurrence_detail_view, name="occurrence_detail"),  # GET, PUT, DELETE
    path("api/occurrences/", occurrences_views.occurrences_view, name="occurrences"),  # GET (listar), POST (criar)
    
    # Filtros: Viagens
    path("api/travels/", travels_views.listar_travels, name="listar_travels"),

    # Dashboard
    path("api/dashboard/unit-summary/", dashboard_views.unit_summary, name="dashboard_unit_summary"),
    path("api/dashboard/occurrence-summary/", dashboard_views.occurrence_summary, name="dashboard_occurrence_summary"),

    path('bigquery/view/diaria', criar_view_diaria, name='criar_view_diaria'),
    path('bigquery/view/mensal', criar_view_mensal, name='criar_view_mensal'),
    path('bigquery/view/exportar', exportar_view, name='exportar_view'),
 
]
