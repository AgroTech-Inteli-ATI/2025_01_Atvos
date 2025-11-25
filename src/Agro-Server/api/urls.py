"""
Mapeamento das rotas públicas da API Agro-Server.
"""
from django.urls import path

from . import (
    bigquery_views,
    bills_views,
    dashboard_views,
    occurrences_views,
    storage_views,
    travels_views,
    units_views,
)
from .root_view import api_root

urlpatterns = [
    # Root
    path("", api_root, name="api_root"),

    # BigQuery
    path("api/bigquery/inserir/", bigquery_views.inserir_registro, name="inserir_registro"),
    path("api/bigquery/atualizar/", bigquery_views.atualizar_registro, name="atualizar_registro"),
    path("api/bigquery/remover/", bigquery_views.remover_registro, name="remover_registro"),
    path("api/bigquery/processar-raw/", bigquery_views.processar_arquivo_raw, name="processar_arquivo_raw"),
    path("api/bigquery/view-diaria/", bigquery_views.criar_view_diaria, name="criar_view_diaria"),
    path("api/bigquery/view-mensal/", bigquery_views.criar_view_mensal, name="criar_view_mensal"),
    path("api/bigquery/exportar-view/", bigquery_views.exportar_view, name="exportar_view"),

    # Storage
    path("api/storage/inserir/", storage_views.upload_arquivo, name="upload_arquivo"),
    path("api/storage/remover/", storage_views.remover_arquivo, name="remover_arquivo"),
    path("api/storage/download/", storage_views.download_arquivo, name="download_arquivo"),

    # Travels & bills
    path("api/travels/", travels_views.listar_travels, name="listar_travels"),
    path("api/bills/", bills_views.listar_bills, name="listar_bills"),

    # Dashboard
    path("api/dashboard/unit-summary/", dashboard_views.unit_summary, name="dashboard_unit_summary"),
    path("api/dashboard/occurrence-summary/", dashboard_views.occurrence_summary, name="dashboard_occurrence_summary"),
    path("api/dashboard/travel-summary/", dashboard_views.travel_summary, name="dashboard_travel_summary"),
    path("api/dashboard/cost-evolution/", dashboard_views.cost_evolution, name="dashboard_cost_evolution"),

    # Units
    path("api/units/", units_views.unidades_view, name="unidades_view"),
    path("api/units/<int:unit_id>/", units_views.unidade_detail_view, name="unidade_detail_view"),
    path("api/units/<int:unit_id>/stats/", units_views.stats_unit, name="stats_unit"),

    # Occurrences
    path("api/occurrences/", occurrences_views.occurrences_view, name="occurrences_view"),
    path("api/occurrences/<int:occurrence_id>/", occurrences_views.occurrence_detail_view, name="occurrence_detail_view"),
    path("api/occurrences/categories/", occurrences_views.listar_categories, name="listar_categories"),
    path("api/occurrences/stats/", occurrences_views.stats_occurrences, name="stats_occurrences"),
]
