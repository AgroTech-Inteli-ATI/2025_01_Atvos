"""
Endpoint raiz da API Agro-Server.
"""
from django.http import JsonResponse


def api_root(request):
    """
    Retorna um resumo da API e links úteis para navegação.
    """
    return JsonResponse(
        {
            "nome": "Agro-Server API",
            "versao": "1.0",
            "documentacao": "Consulte README.md para mais detalhes.",
            "endpoints": {
                "bigquery": [
                    "/api/bigquery/inserir/",
                    "/api/bigquery/atualizar/",
                    "/api/bigquery/remover/",
                    "/api/bigquery/processar-raw/",
                    "/api/bigquery/view-diaria/",
                    "/api/bigquery/view-mensal/",
                    "/api/bigquery/exportar-view/",
                ],
                "storage": [
                    "/api/storage/inserir/",
                    "/api/storage/remover/",
                    "/api/storage/download/",
                ],
                "travels": [
                    "/api/travels/",
                    "/api/dashboard/travel-summary/",
                    "/api/dashboard/cost-evolution/",
                ],
                "units": [
                    "/api/units/",
                    "/api/units/<id>/",
                    "/api/units/<id>/stats/",
                ],
                "occurrences": [
                    "/api/occurrences/",
                    "/api/occurrences/<id>/",
                    "/api/occurrences/categories/",
                    "/api/occurrences/stats/",
                ],
                "bills": ["/api/bills/"],
            },
        }
    )
"""
View para a rota raiz da API
"""
from django.http import JsonResponse

def api_root(request):
    """
    Retorna informações sobre a API e endpoints disponíveis
    """
    return JsonResponse({
        "nome": "Agro-Server API",
        "versao": "1.0",
        "descricao": "API para gerenciamento de dados agrícolas com BigQuery e Cloud Storage",
        "endpoints": {
            "bigquery": {
                "inserir": "/bigquery/inserir/",
                "atualizar": "/bigquery/atualizar/",
                "remover": "/bigquery/remover/",
                "processar_raw": "/bigquery/processar-raw/",
                "view_diaria": "/bigquery/view-diaria/",
                "view_mensal": "/bigquery/view-mensal/",
                "exportar_view": "/bigquery/exportar-view/"
            },
            "storage": {
                "upload": "/storage/inserir/",
                "remover": "/storage/remover/",
                "download": "/storage/download/"
            },
            "travels": {
                "listar": "/travels/"
            },
            "units": {
                "listar_criar": "/units/",
                "detalhes": "/units/<id>/",
                "estatisticas": "/units/<id>/stats/"
            },
            "occurrences": {
                "listar_criar": "/occurrences/",
                "detalhes": "/occurrences/<id>/",
                "categorias": "/occurrences/categories/",
                "estatisticas": "/occurrences/stats/"
            }
        }
    })

