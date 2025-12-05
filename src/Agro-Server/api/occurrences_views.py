"""
Views para rotas de Ocorrências
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from clients.bigquery_client import BigQueryClient
from utils.validators import validar_occurrence, validar_id

client = BigQueryClient()
TABLE_NAME = "occurrence"
CATEGORY_TABLE = "occurrence_category"

@csrf_exempt
def occurrences_view(request, occurrence_id=None):
    """View unificada para /api/occurrences/ - trata GET (listar) e POST (criar)"""
    if request.method == "GET":
        return listar_occurrences(request)
    elif request.method == "POST":
        return criar_occurrence(request)
    else:
        return JsonResponse({"erro": "Método não permitido"}, status=405)

def listar_occurrences(request):
    """GET /api/occurrences - Lista todas as ocorrências (com suporte a filtro unit_id)"""
    
    try:
        limit = request.GET.get("limit")
        offset = request.GET.get("offset", 0)
        unit_id = request.GET.get("unit_id")
        
        limit = int(limit) if limit else None
        offset = int(offset) if offset else 0
        
        # Se tiver filtro unit_id, usa filtrar, senão usa listar
        if unit_id:
            filters = {"unit_id": unit_id}
            occurrences = client.filtrar(TABLE_NAME, filters, limit=limit, offset=offset)
        else:
            occurrences = client.listar(TABLE_NAME, limit=limit, offset=offset)
        
        return JsonResponse({
            "status": "ok",
            "data": occurrences,
            "count": len(occurrences)
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def occurrence_detail_view(request, occurrence_id):
    """View unificada para /api/occurrences/{id}/ - trata GET, PUT, DELETE"""
    if request.method == "GET":
        return buscar_occurrence(request, occurrence_id)
    elif request.method == "PUT":
        return atualizar_occurrence(request, occurrence_id)
    elif request.method == "DELETE":
        return remover_occurrence(request, occurrence_id)
    else:
        return JsonResponse({"erro": "Método não permitido"}, status=405)

def buscar_occurrence(request, occurrence_id):
    """GET /api/occurrences/{id} - Detalhes de uma ocorrência"""
    
    try:
        valido, msg = validar_id(occurrence_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        occurrence = client.buscar_por_id(TABLE_NAME, str(occurrence_id))
        
        if not occurrence:
            return JsonResponse({"erro": "Ocorrência não encontrada"}, status=404)
        
        return JsonResponse({
            "status": "ok",
            "data": occurrence
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def criar_occurrence(request):
    """POST /api/occurrences - Registra nova ocorrência"""
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validação
        valido, msg = validar_occurrence(data)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Verifica se travel_id, unit_id e category_id existem
        travel = client.buscar_por_id("TRAVEL", str(data["travel_id"]))
        if not travel:
            return JsonResponse({"erro": "Viagem (travel_id) não encontrada"}, status=400)
        
        unit = client.buscar_por_id("UNIT", str(data["unit_id"]))
        if not unit:
            return JsonResponse({"erro": "Unidade (unit_id) não encontrada"}, status=400)
        
        category = client.buscar_por_id(CATEGORY_TABLE, str(data["category_id"]))
        if not category:
            return JsonResponse({"erro": "Categoria (category_id) não encontrada"}, status=400)
        
        # Prepara dados para inserção
        row = {
            "travel_id": str(data["travel_id"]),
            "unit_id": str(data["unit_id"]),
            "category_id": str(data["category_id"]),
            "datetime": data["datetime"],
            "carrier_name": data.get("carrier_name", ""),
            "root_cause": data.get("root_cause", ""),
            "description": data.get("description", "")
        }
        
        # Gera ID se não fornecido
        if "id" not in data:
            existing = client.listar(TABLE_NAME, limit=1000)
            if existing:
                max_id = max([int(o.get("id", 0)) for o in existing if o.get("id")], default=0)
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
def atualizar_occurrence(request, occurrence_id):
    """PUT /api/occurrences/{id} - Atualiza ocorrência"""
    if request.method != "PUT":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        valido, msg = validar_id(occurrence_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Verifica se existe
        occurrence = client.buscar_por_id(TABLE_NAME, str(occurrence_id))
        if not occurrence:
            return JsonResponse({"erro": "Ocorrência não encontrada"}, status=404)
        
        data = json.loads(request.body)
        
        # Valida campos opcionais se presentes
        if "travel_id" in data:
            travel = client.buscar_por_id("TRAVEL", str(data["travel_id"]))
            if not travel:
                return JsonResponse({"erro": "Viagem (travel_id) não encontrada"}, status=400)
        
        if "unit_id" in data:
            unit = client.buscar_por_id("UNIT", str(data["unit_id"]))
            if not unit:
                return JsonResponse({"erro": "Unidade (unit_id) não encontrada"}, status=400)
        
        if "category_id" in data:
            category = client.buscar_por_id(CATEGORY_TABLE, str(data["category_id"]))
            if not category:
                return JsonResponse({"erro": "Categoria (category_id) não encontrada"}, status=400)
        
        # Prepara atualizações
        updates = {}
        campos_permitidos = ["travel_id", "unit_id", "category_id", "datetime", 
                            "carrier_name", "root_cause", "description"]
        
        for campo in campos_permitidos:
            if campo in data:
                updates[campo] = data[campo] if data[campo] is not None else ""
        
        if not updates:
            return JsonResponse({"erro": "Nenhum campo para atualizar"}, status=400)
        
        resultado = client.atualizar(str(occurrence_id), updates, TABLE_NAME)
        
        # Busca o registro atualizado
        occurrence_atualizada = client.buscar_por_id(TABLE_NAME, str(occurrence_id))
        
        return JsonResponse({
            "status": "ok",
            "data": occurrence_atualizada
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def remover_occurrence(request, occurrence_id):
    """DELETE /api/occurrences/{id} - Remove ocorrência"""
    if request.method != "DELETE":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        valido, msg = validar_id(occurrence_id)
        if not valido:
            return JsonResponse({"erro": msg}, status=400)
        
        # Verifica se existe
        occurrence = client.buscar_por_id(TABLE_NAME, str(occurrence_id))
        if not occurrence:
            return JsonResponse({"erro": "Ocorrência não encontrada"}, status=404)
        
        resultado = client.remover(str(occurrence_id), TABLE_NAME)
        
        return JsonResponse({
            "status": "ok",
            "message": "Ocorrência removida com sucesso"
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def listar_categories(request):
    """GET /api/occurrences/categories - Lista categorias de ocorrências"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        categories = client.listar(CATEGORY_TABLE)
        
        return JsonResponse({
            "status": "ok",
            "data": categories,
            "count": len(categories)
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def stats_occurrences(request):
    """GET /api/occurrences/stats - Estatísticas agregadas de ocorrências"""
    if request.method != "GET":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        # Estatísticas por categoria
        query_categoria = f"""
        SELECT 
            oc.category_id,
            cat.name as category_name,
            COUNT(*) as total
        FROM `{client.table_ref(TABLE_NAME)}` oc
        LEFT JOIN `{client.table_ref(CATEGORY_TABLE)}` cat ON oc.category_id = cat.id
        GROUP BY oc.category_id, cat.name
        ORDER BY total DESC
        """
        
        # Estatísticas por unidade
        query_unidade = f"""
        SELECT 
            o.unit_id,
            u.name as unit_name,
            COUNT(*) as total
        FROM `{client.table_ref(TABLE_NAME)}` o
        LEFT JOIN `{client.table_ref("UNIT")}` u ON o.unit_id = u.id
        GROUP BY o.unit_id, u.name
        ORDER BY total DESC
        """
        
        # Total geral
        query_total = f"""
        SELECT COUNT(*) as total_geral
        FROM `{client.table_ref(TABLE_NAME)}`
        """
        
        stats_categoria = client.executar_query(query_categoria)
        stats_unidade = client.executar_query(query_unidade)
        stats_total = client.executar_query(query_total)
        
        stats = {
            "total_geral": stats_total[0].get("total_geral", 0) if stats_total else 0,
            "por_categoria": [
                {
                    "category_id": int(row.get("category_id", 0)),
                    "category_name": row.get("category_name", ""),
                    "total": row.get("total", 0)
                }
                for row in stats_categoria
            ],
            "por_unidade": [
                {
                    "unit_id": int(row.get("unit_id", 0)),
                    "unit_name": row.get("unit_name", ""),
                    "total": row.get("total", 0)
                }
                for row in stats_unidade
            ]
        }
        
        return JsonResponse({
            "status": "ok",
            "data": stats
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

