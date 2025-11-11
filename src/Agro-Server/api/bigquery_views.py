from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from clients.bigquery_client import BigQueryClient
from .etl_service import EtlService


client = BigQueryClient()  # instância única para todas as rotas

@csrf_exempt
def processar_arquivo_raw(request):
    """
    Essa rota aciona o serviço de ETL para processar um arquivo bruto do Cloud Storage.
    Espera um JSON com o nome do blob a ser processado.

    Exemplo de JSON:
    {
        "blob_name": "raw/nome_do_arquivo.csv"
    }
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        blob_name = data.get("blob_name")

        if not blob_name:
            return JsonResponse({"erro": "O campo 'blob_name' é obrigatório."}, status=400)

        etl_service = EtlService()
        resultado = etl_service.process_raw_file(blob_name)

        if resultado["status"] == "error":
            return JsonResponse(resultado, status=500)

        return JsonResponse(resultado)

    except Exception as e:
        return JsonResponse({"erro": f"Erro inesperado na view: {e}"}, status=500)


@csrf_exempt
def inserir_registro(request):
    """
    Essa rota é responsável por inserir dados em uma tabela "x" no BigQuery

    Exemplo de JSON Para essa rota:
    {
        "table_id": "users",
        "row": {
        "id": "u3333333-cccc-dddd-eeee-333333333333",
        "name": "Isabelle Clubes Central",
        "email": "isa.clubes@example.com",
        "senha": "123",
        "created_at": "2025-10-28T08:30:00Z",
        "updated_at": "2025-10-28T08:45:00Z",
        "active": false
        }
    }

    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    try:
        data = json.loads(request.body)
        row = data.get("row")
        table_id = data.get("table_id")
        resultado = client.inserir(row, table_id)
        return JsonResponse(resultado)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def atualizar_registro(request):
    """
    
    
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    try:
        data = json.loads(request.body)
        row_id = data.pop("id")  # remove o id do dict
        updates = data.pop("updates")
        table_id = data.get("table_id")
        resultado = client.atualizar(row_id, updates, table_id)
        return JsonResponse(resultado)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def remover_registro(request):
    """
    Essa rota é responsável por remover dados em uma tabela "x" no BigQuery

    Exemplo de JSON Para essa rota:
    {
        "table_id": "users",
        "id": "u5555555-cccc-dddd-ffff-333333333333"
    }

    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    try:
        data = json.loads(request.body)
        row_id = data.get("id")
        table_id = data.get("table_id")
        resultado = client.remover(row_id, table_id)
        return JsonResponse(resultado)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
