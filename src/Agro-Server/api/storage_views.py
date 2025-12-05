# api/storage_views.py
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from clients.storage_client import CloudStorageClient

client = CloudStorageClient()


@csrf_exempt
def upload_arquivo(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        if "file" not in request.FILES:
            return JsonResponse({"erro": "Arquivo não enviado. Use o campo 'file' no formulário."}, status=400)

        file = request.FILES["file"]
        destination_blob = request.POST.get("destination_blob")

        if not destination_blob:
            return JsonResponse({"erro": "Campo 'destination_blob' é obrigatório."}, status=400)

        file_bytes = file.read()
        resultado = client.upload_buffer(file_bytes, destination_blob)
        return JsonResponse(resultado)

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


@csrf_exempt
def remover_arquivo(request):
    """
    Essa rota é responsável por remover um arquivo no Bucket a partir de uma URL


    Exemplo de json:

    {
        "blob_name": "raw/KM CAPTURADO PELA TELEMETRIA - 05 as 10h.jpg"
    }
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        blob_name = data.get("blob_name")

        if not blob_name:
            return JsonResponse({"erro": "Campo 'blob_name' é obrigatório."}, status=400)

        resultado = client.delete_file(blob_name)
        return JsonResponse(resultado)

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


@csrf_exempt
def download_arquivo(request):
    """
    Essa rota é responsável por conferir uma URL no Bucket e fazer o download do arquivo no Buffer


    Exemplo de json:

    {
        "blob_name": "raw/KM CAPTURADO PELA TELEMETRIA - 05 as 10h.jpg"
    }
    """
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        blob_name = data.get("blob_name")

        if not blob_name:
            return JsonResponse({"erro": "Campo 'blob_name' é obrigatório."}, status=400)

        file_bytes = client.download_buffer(blob_name)

        # Cria uma resposta binária
        response = HttpResponse(file_bytes, content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{blob_name.split("/")[-1]}"'
        return response

    except FileNotFoundError as e:
        return JsonResponse({"erro": str(e)}, status=404)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
