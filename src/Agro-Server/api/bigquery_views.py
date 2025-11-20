from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from clients.bigquery_client import BigQueryClient

client = BigQueryClient()  # instância única para todas as rotas

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

@csrf_exempt
def criar_view_diaria(request):
    """
    Cria/atualiza view D-1 no BigQuery com dados consolidados do dia anterior
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        sql_view = """
        CREATE OR REPLACE VIEW `{project}.{dataset}.view_diaria_d_minus_1` AS
        SELECT
            DATE(processed_at) AS ds,
            veiculo_id,
            SUM(km_variavel) AS km_total,
            SUM(custos_consolidados) AS custo_total,
            AVG(score) AS avg_score,
            COUNT(1) AS total_viagens
        FROM `{project}.{dataset}.viagens_cleaned`
        WHERE DATE(processed_at) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
        GROUP BY ds, veiculo_id
        """
        
        resultado = client.execute_query(sql_view)
        return JsonResponse({"mensagem": "View diária criada/atualizada com sucesso"})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def criar_view_mensal(request):
    """
    Cria/atualiza view mensal no BigQuery com dados consolidados do mês
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        sql_view = """
        CREATE OR REPLACE VIEW `{project}.{dataset}.view_mensal_consolidado` AS
        SELECT
            FORMAT_DATE('%Y-%m', DATE(processed_at)) AS ano_mes,
            veiculo_id,
            SUM(km_variavel) AS km_mes,
            SUM(custos_consolidados) AS custo_mes,
            AVG(score) AS avg_score,
            COUNT(1) AS total_viagens,
            COUNT(DISTINCT DATE(processed_at)) AS dias_operacao
        FROM `{project}.{dataset}.viagens_cleaned`
        WHERE DATE(processed_at) >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
        GROUP BY ano_mes, veiculo_id
        """
        
        resultado = client.execute_query(sql_view)
        return JsonResponse({"mensagem": "View mensal criada/atualizada com sucesso"})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)

@csrf_exempt
def exportar_view(request):
    """
    Exporta uma view específica do BigQuery para CSV
    
    Exemplo de JSON para essa rota:
    {
        "view_name": "view_diaria_d_minus_1",
        "format": "CSV"  # ou "EXCEL"
    }
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        view_name = data.get("view_name")
        format_type = data.get("format", "CSV")
        
        # Executa query na view
        sql = f"SELECT * FROM `{client.project}.{client.dataset}.{view_name}`"
        df = client.query_to_dataframe(sql)
        
        # Gera arquivo temporário
        if format_type.upper() == "CSV":
            file_path = f"/tmp/{view_name}.csv"
            df.to_csv(file_path, index=False)
        else:  # EXCEL
            file_path = f"/tmp/{view_name}.xlsx"
            df.to_excel(file_path, index=False)
            
        # TODO: Implementar lógica para download do arquivo
        return JsonResponse({
            "mensagem": f"Dados exportados para {format_type}",
            "arquivo": file_path
        })
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
