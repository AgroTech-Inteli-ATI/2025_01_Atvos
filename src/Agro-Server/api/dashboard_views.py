"""
Views para rotas de dashboard (métricas agregadas)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from clients.bigquery_client import BigQueryClient

client = BigQueryClient()


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
        FROM `{client.table_ref("UNIT")}` u
        LEFT JOIN `{client.table_ref("TRAVEL")}` t ON t.unit_id = u.id
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
        FROM `{client.table_ref("OCCURRENCE_CATEGORY")}` cat
        LEFT JOIN `{client.table_ref("OCCURRENCE")}` occ ON occ.category_id = cat.id
        GROUP BY cat.id, cat.name
        ORDER BY total_ocorrencias DESC
        """

        query_total = f"""
        SELECT COUNT(*) AS total_ocorrencias
        FROM `{client.table_ref("OCCURRENCE")}`
        """

        categorias = client.executar_query(query_categoria)
        total_result = client.executar_query(query_total)

        data = {
            "total_ocorrencias": total_result[0].get("total_ocorrencias", 0) if total_result else 0,
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


