"""
Views para rotas de Unidades Operacionais
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from clients.bigquery_client import BigQueryClient
from utils.validators import validar_unit, validar_id

client = BigQueryClient()
TABLE_NAME = "unit"

@csrf_exempt
def unidades_view(request, unit_id=None):
    """View unificada para /api/units/ - trata GET (listar) e POST (criar)"""
    if request.method == "GET":
        return listar_units(request)
    elif request.method == "POST":
        return criar_unit(request)
    else:
        return JsonResponse({"erro": "Método não permitido"}, status=405)

def listar_units(request):
    """GET /api/units - Lista todas as unidades"""
    
    try:
        limit = request.GET.get("limit")
        offset = request.GET.get("offset", 0)
        
        limit = int(limit) if limit else None
        offset = int(offset) if offset else 0
        
        units = client.listar(TABLE_NAME, limit=limit, offset=offset)
        
        return JsonResponse({
            "status": "ok",
            "data": units,
            "count": len(units)
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def unidade_detail_view(request, unit_id):
    """View unificada para /api/units/{id}/ - trata GET, PUT, DELETE"""
    if request.method == "GET":
        return buscar_unit(request, unit_id)
    elif request.method == "PUT":
        return atualizar_unit(request, unit_id)
    elif request.method == "DELETE":
        return remover_unit(request, unit_id)
    else:
        return JsonResponse({"erro": "Método não permitido"}, status=405)

def buscar_unit(request, unit_id):
    """GET /api/units/{id} - Detalhes de uma unidade"""
    
    try:
        valido, msg = validar_id(unit_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        unit = client.buscar_por_id(TABLE_NAME, str(unit_id))
        
        if not unit:
            return JsonResponse({"erro": "Unidade não encontrada"}, status=404)
        
        return JsonResponse({
            "status": "ok",
            "data": unit
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def criar_unit(request):
    """POST /api/units - Cria nova unidade"""
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validação
        valido, msg = validar_unit(data)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Prepara dados para inserção
        row = {
            "name": data.get("name"),
            "description": data.get("description", "")
        }
        
        # Se não tiver ID, o BigQueryClient gera UUID, mas para UNIT precisamos de int
        # Vamos buscar o próximo ID disponível
        if "id" not in data:
            # Busca o maior ID existente e incrementa
            existing = client.listar(TABLE_NAME, limit=1000)
            if existing:
                max_id = max([int(u.get("id", 0)) for u in existing if u.get("id")], default=0)
                row["id"] = str(max_id + 1)
            else:
                row["id"] = "1"
        else:
            row["id"] = str(data["id"])
        
        resultado = client.inserir(row, TABLE_NAME)
        
        return JsonResponse({
            "status": "ok",
            "data": resultado.get("row")
        }, status=201)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def atualizar_unit(request, unit_id):
    """PUT /api/units/{id} - Atualiza unidade"""
    if request.method != "PUT":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        valido, msg = validar_id(unit_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Verifica se existe
        unit = client.buscar_por_id(TABLE_NAME, str(unit_id))
        if not unit:
            return JsonResponse({"erro": "Unidade não encontrada"}, status=404)
        
        data = json.loads(request.body)
        
        # Validação
        valido, msg = validar_unit(data)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Prepara atualizações (remove id se presente)
        updates = {}
        if "name" in data:
            updates["name"] = data["name"]
        if "description" in data:
            updates["description"] = data.get("description", "")
        
        if not updates:
            return JsonResponse({"erro": "Nenhum campo para atualizar"}, status=400)
        
        resultado = client.atualizar(str(unit_id), updates, TABLE_NAME)
        
        # Busca o registro atualizado
        unit_atualizada = client.buscar_por_id(TABLE_NAME, str(unit_id))
        
        return JsonResponse({
            "status": "ok",
            "data": unit_atualizada
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def remover_unit(request, unit_id):
    """DELETE /api/units/{id} - Remove unidade"""
    if request.method != "DELETE":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        valido, msg = validar_id(unit_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Verifica se existe
        unit = client.buscar_por_id(TABLE_NAME, str(unit_id))
        if not unit:
            return JsonResponse({"erro": "Unidade não encontrada"}, status=404)
        
        resultado = client.remover(str(unit_id), TABLE_NAME)
        
        return JsonResponse({
            "status": "ok",
            "message": "Unidade removida com sucesso"
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def stats_unit(request, unit_id):
    """GET /api/units/{id}/stats - Estatísticas da unidade (KM, ocorrências)"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        valido, msg = validar_id(unit_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Verifica se a unidade existe
        unit = client.buscar_por_id(TABLE_NAME, str(unit_id))
        if not unit:
            return JsonResponse({"erro": "Unidade não encontrada"}, status=404)
        
        # Query para estatísticas de viagens (KM total)
        query_travels = f"""
        SELECT 
            COUNT(*) as total_viagens,
            COALESCE(SUM(full_distance), 0) as total_km
        FROM `{client.table_ref("TRAVEL")}`
        WHERE unit_id = {unit_id}
        """
        
        # Query para estatísticas de ocorrências
        query_occurrences = f"""
        SELECT 
            COUNT(*) as total_ocorrencias
        FROM `{client.table_ref("OCCURRENCE")}`
        WHERE unit_id = {unit_id}
        """
        
        travels_stats = client.executar_query(query_travels)
        occurrences_stats = client.executar_query(query_occurrences)
        
        stats = {
            "unit_id": unit_id,
            "unit_name": unit.get("name"),
            "total_viagens": travels_stats[0].get("total_viagens", 0) if travels_stats else 0,
            "total_km": float(travels_stats[0].get("total_km", 0)) if travels_stats else 0.0,
            "total_ocorrencias": occurrences_stats[0].get("total_ocorrencias", 0) if occurrences_stats else 0
        }
        
        return JsonResponse({
            "status": "ok",
            "data": stats
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

