"""
Views para rotas de Viagens (Travels)
"""
from typing import List

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.api_core import exceptions as gcloud_exceptions

from clients.bigquery_client import BigQueryClient
from .helpers import build_datetime_filters, parse_iso_datetime

client = BigQueryClient()

TABLE_NAME = "TRAVEL"
UNIT_TABLE = "UNIT"
BILL_TABLE = "BILL"

_COST_EXPRESSION = (
    "COALESCE(b.total_cost, b.fix_cost + COALESCE(b.variable_km, 0) * "
    "COALESCE(t.full_distance, 0), 0)"
)


def _build_travel_filters(request) -> List[str]:
    start_dt = parse_iso_datetime(request.GET.get("start_date"))
    end_dt = parse_iso_datetime(request.GET.get("end_date"))
    filters = build_datetime_filters("t.datetime", start_dt, end_dt)

    unit_id = request.GET.get("unit_id")
    if unit_id:
        filters.append(f"t.unit_id = '{unit_id}'")
    return filters


def _build_travel_query(where_clause: str, include_bill: bool) -> str:
    cost_select = (
        f"{_COST_EXPRESSION} AS bill_total_cost, b.fix_cost, b.variable_km"
        if include_bill
        else "NULL AS bill_total_cost, NULL AS fix_cost, NULL AS variable_km"
    )
    bill_join = (
        f"LEFT JOIN `{client.table_ref(BILL_TABLE)}` b ON b.travel_id = t.id"
        if include_bill
        else ""
    )

    return f"""
        SELECT
            t.id,
            t.datetime,
            t.license_plate,
            t.asset_description,
            t.register_number,
            t.garage_name,
            t.full_distance,
            t.unit_id,
            u.name AS unit_name,
            {cost_select}
        FROM `{client.table_ref(TABLE_NAME)}` t
        LEFT JOIN `{client.table_ref(UNIT_TABLE)}` u ON u.id = t.unit_id
        {bill_join}
        {where_clause}
        ORDER BY t.datetime DESC
    """


@csrf_exempt
def listar_travels(request):
    """GET /api/travels - Lista viagens com filtros de data."""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        limit = request.GET.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100

        filters = _build_travel_filters(request)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        query_with_bill = _build_travel_query(where_clause, include_bill=True) + f" LIMIT {limit_value}"
        query_without_bill = _build_travel_query(where_clause, include_bill=False) + f" LIMIT {limit_value}"

        try:
            results = client.executar_query(query_with_bill)
            bill_available = True
        except gcloud_exceptions.NotFound:
            results = client.executar_query(query_without_bill)
            bill_available = False

        for row in results:
            full_distance = row.get("full_distance")
            if full_distance is not None:
                row["full_distance"] = float(full_distance)

            bill_cost = row.get("bill_total_cost")
            if bill_cost is not None:
                row["bill.total_cost"] = float(bill_cost)
                row["total_cost"] = float(bill_cost)
            else:
                row["bill.total_cost"] = None
                row["total_cost"] = None

        return JsonResponse(
            {
                "status": "ok",
                "data": results,
                "count": len(results),
                "bill_table_available": bill_available,
            }
        )
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
