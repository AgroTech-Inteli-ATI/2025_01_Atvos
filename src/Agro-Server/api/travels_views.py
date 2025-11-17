"""
Views para rotas de Viagens (Travels)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from clients.bigquery_client import BigQueryClient

client = BigQueryClient()
TABLE_NAME = "TRAVEL"

@csrf_exempt
def listar_travels(request):
    """GET /api/travels - Lista viagens (com suporte a filtro unit_id)"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        limit = request.GET.get("limit")
        offset = request.GET.get("offset", 0)
        unit_id = request.GET.get("unit_id")
        
        limit = int(limit) if limit else None
        offset = int(offset) if offset else 0
        
        # Se tiver filtro unit_id, usa filtrar, senão usa listar
        if unit_id:
            filters = {"unit_id": unit_id}
            travels = client.filtrar(TABLE_NAME, filters, limit=limit, offset=offset)
        else:
            travels = client.listar(TABLE_NAME, limit=limit, offset=offset)
        
        return JsonResponse({
            "status": "ok",
            "data": travels,
            "count": len(travels)
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

