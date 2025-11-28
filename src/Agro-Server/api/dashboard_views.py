"""
Views para rotas de dashboard (métricas agregadas)
"""
from typing import List

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.api_core import exceptions as gcloud_exceptions

from clients.bigquery_client import BigQueryClient
from .helpers import build_datetime_filters, parse_iso_datetime

client = BigQueryClient()

_COST_EXPRESSION = (
    "COALESCE(b.fix_cost + COALESCE(b.variable_km, 0) * COALESCE(t.full_distance, 0), 0)"
)


def _build_common_filters(request) -> List[str]:
    start_dt = parse_iso_datetime(request.GET.get("start_date"))
    end_dt = parse_iso_datetime(request.GET.get("end_date"))
    filters = build_datetime_filters("t.datetime", start_dt, end_dt)

    unit_id = request.GET.get("unit_id")
    if unit_id:
        filters.append(f"t.unit_id = '{unit_id}'")
    return filters


@csrf_exempt
def unit_summary(request):
    """GET /api/dashboard/unit-summary - KM por unidade"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        query = f"""
        SELECT 
            u.id AS unit_id,
            u.name AS unit_name,
            COUNT(t.id) AS total_viagens,
            COALESCE(SUM(t.full_distance), 0) AS total_km
        FROM `{client.table_ref("unit")}` u
        LEFT JOIN `{client.table_ref("travel")}` t ON t.unit_id = u.id
        GROUP BY u.id, u.name
        ORDER BY u.name
        """

        results = client.executar_query(query)
        data = [
            {
                "unit_id": row.get("unit_id"),
                "unit_name": row.get("unit_name", ""),
                "total_viagens": row.get("total_viagens", 0),
                "total_km": float(row.get("total_km", 0.0)),
            }
            for row in results
        ]

        return JsonResponse({"status": "ok", "data": data})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


@csrf_exempt
def occurrence_summary(request):
    """GET /api/dashboard/occurrence-summary - Número e categorias de ocorrências"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        query_categoria = f"""
        SELECT 
            cat.id AS category_id,
            cat.name AS category_name,
            COUNT(occ.id) AS total_ocorrencias
        FROM `{client.table_ref("occurrence_category")}` cat
        LEFT JOIN `{client.table_ref("occurrence")}` occ ON occ.category_id = cat.id
        GROUP BY cat.id, cat.name
        ORDER BY total_ocorrencias DESC
        """

        query_total = f"""
        SELECT COUNT(*) AS total_ocorrencias
        FROM `{client.table_ref("occurrence")}`
        """

        categorias = client.executar_query(query_categoria)
        total_result = client.executar_query(query_total)

        data = {
            "total_ocorrencias": total_result[0].get("total_ocorrencias", 0)
            if total_result
            else 0,
            "por_categoria": [
                {
                    "category_id": row.get("category_id"),
                    "category_name": row.get("category_name", ""),
                    "total_ocorrencias": row.get("total_ocorrencias", 0),
                }
                for row in categorias
            ],
        }

        return JsonResponse({"status": "ok", "data": data})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


@csrf_exempt
def travel_summary(request):
    """GET /api/dashboard/travel-summary - KPIs principais"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        print("\nSEGUE AQUI O REQUEST DE TRAVEL SUMMARY: ", request)

        # =======================================================
        # 1) MONTA OS FILTROS (AGORA ANTES DA DEBUG QUERY)
        # =======================================================
        filters = _build_common_filters(request)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        # =======================================================
        # 2) QUERY DE DEBUG — COM OS MESMOS FILTROS
        # =======================================================
        debug_query = f"""
        SELECT
            t.id AS travel_id_from_travel,
            b.travel_id AS travel_id_from_bill,
            t.datetime
        FROM `{client.table_ref("travel")}` t
        LEFT JOIN `{client.table_ref("bill")}` b ON b.travel_id = t.id
        {where_clause}
        LIMIT 20
        """

        print("\n🔎 Rodando QUERY DE DEBUG para verificar JOIN:")
        print(debug_query)

        try:
            debug_results = client.executar_query(debug_query)
        except Exception as e:
            print("⚠️ Erro na query de debug:", e)
            debug_results = []

        print("\n🔥 RESULTADOS DA QUERY DE DEBUG (t.id e b.travel_id):")
        for r in debug_results:
            print("   ➤", r)

        # =======================================================
        # 3) QUERY PRINCIPAL
        # =======================================================

        query = f"""
        SELECT
            COUNT(t.id) AS total_travels,
            COALESCE(SUM(t.full_distance), 0) AS total_distance_km,
            COALESCE(SUM({_COST_EXPRESSION}), 0) AS total_cost
        FROM `{client.table_ref("travel")}` t
        LEFT JOIN `{client.table_ref("bill")}` b ON b.travel_id = t.id
        {where_clause}
        """

        try:
            results = client.executar_query(query)
        except gcloud_exceptions.NotFound:
            fallback_query = f"""
            SELECT
                COUNT(t.id) AS total_travels,
                COALESCE(SUM(t.full_distance), 0) AS total_distance_km,
                0 AS total_cost
            FROM `{client.table_ref("travel")}` t
            {where_clause}
            """
            results = client.executar_query(fallback_query)

        row = results[0] if results else {}

        total_travels = int(row.get("total_travels", 0) or 0)
        total_distance = float(row.get("total_distance_km", 0.0) or 0.0)
        total_cost = float(row.get("total_cost", 0.0) or 0.0)

        data = {
            "total_travels": total_travels,
            "total_distance_km": total_distance,
            "total_cost": total_cost,
            "avg_cost_per_travel": total_cost / total_travels if total_travels else 0.0,
            "avg_distance_per_travel": total_distance / total_travels if total_travels else 0.0,
        }

        return JsonResponse({"status": "ok", "data": data})

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)



@csrf_exempt
def cost_evolution(request):
    """GET /api/dashboard/cost-evolution - Série temporal de custos"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    period = request.GET.get("period", "month").lower()
    limit = request.GET.get("limit")
    try:
        limit_value = int(limit) if limit else None
    except ValueError:
        limit_value = None

    if period == "week":
        period_label = "FORMAT_TIMESTAMP('%G-%V', t.datetime)"
    elif period == "day":
        period_label = "FORMAT_TIMESTAMP('%Y-%m-%d', t.datetime)"
    else:
        period_label = "FORMAT_TIMESTAMP('%Y-%m', t.datetime)"

    try:
        filters = _build_common_filters(request)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        query = f"""
        SELECT
            {period_label} AS period_label,
            DATE(MIN(t.datetime)) AS period_start,
            COUNT(t.id) AS total_travels,
            COALESCE(SUM(t.full_distance), 0) AS total_distance_km,
            COALESCE(SUM({_COST_EXPRESSION}), 0) AS total_cost
        FROM `{client.table_ref("travel")}` t
        LEFT JOIN `{client.table_ref("bill")}` b ON b.travel_id = t.id
        {where_clause}
        GROUP BY period_label
        ORDER BY period_start
        """

        if limit_value:
            query += f" LIMIT {limit_value}"

        try:
            results = client.executar_query(query)
        except gcloud_exceptions.NotFound:
            fallback_query = f"""
            SELECT
                {period_label} AS period_label,
                DATE(MIN(t.datetime)) AS period_start,
                COUNT(t.id) AS total_travels,
                COALESCE(SUM(t.full_distance), 0) AS total_distance_km,
                0 AS total_cost
            FROM `{client.table_ref("travel")}` t
            {where_clause}
            GROUP BY period_label
            ORDER BY period_start
            """
            if limit_value:
                fallback_query += f" LIMIT {limit_value}"
            results = client.executar_query(fallback_query)
        data = [
            {
                "period": row.get("period_label"),
                "period_start": row.get("period_start"),
                "total_travels": int(row.get("total_travels", 0) or 0),
                "total_distance_km": float(row.get("total_distance_km", 0.0) or 0.0),
                "total_cost": float(row.get("total_cost", 0.0) or 0.0),
            }
            for row in results
        ]

        return JsonResponse({"status": "ok", "data": data})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
