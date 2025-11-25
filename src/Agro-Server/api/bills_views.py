"""
Views para rotas de faturas (Bills).
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.api_core import exceptions as gcloud_exceptions

from clients.bigquery_client import BigQueryClient
from .helpers import build_datetime_filters, parse_iso_datetime

client = BigQueryClient()

BILL_TABLE = "BILL"
TRAVEL_TABLE = "TRAVEL"


@csrf_exempt
def listar_bills(request):
    """GET /api/bills - Retorna faturas associadas às viagens."""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        start_dt = parse_iso_datetime(request.GET.get("start_date"))
        end_dt = parse_iso_datetime(request.GET.get("end_date"))
        filters = build_datetime_filters("t.datetime", start_dt, end_dt)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        query = f"""
        SELECT
            b.id,
            b.travel_id,
            b.datetime,
            b.fix_cost,
            b.variable_km,
            COALESCE(b.total_cost, b.fix_cost + COALESCE(b.variable_km, 0) * COALESCE(t.full_distance, 0), 0)
                AS total_cost
        FROM `{client.table_ref(BILL_TABLE)}` b
        INNER JOIN `{client.table_ref(TRAVEL_TABLE)}` t ON t.id = b.travel_id
        {where_clause}
        ORDER BY b.datetime DESC
        """

        try:
            results = client.executar_query(query)
        except gcloud_exceptions.NotFound:
            return JsonResponse(
                {
                    "status": "ok",
                    "data": [],
                    "count": 0,
                    "warning": "Tabela BILL não encontrada no BigQuery",
                }
            )
        for row in results:
            if row.get("fix_cost") is not None:
                row["fix_cost"] = float(row["fix_cost"])
            if row.get("variable_km") is not None:
                row["variable_km"] = float(row["variable_km"])
            if row.get("total_cost") is not None:
                row["total_cost"] = float(row["total_cost"])

        return JsonResponse({"status": "ok", "data": results, "count": len(results)})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

