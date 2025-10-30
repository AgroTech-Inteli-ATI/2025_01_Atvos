import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery

# ===========================
# Caminho base e .env
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ===========================
# Django settings básicos
# ===========================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-1234567890")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'api',  # nosso app
]

MIDDLEWARE = []

ROOT_URLCONF = 'api.urls'
TEMPLATES = []
WSGI_APPLICATION = 'api.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===========================
# BigQuery settings
# ===========================
# 1. Pega o caminho do arquivo JSON da service account do .env
BIGQUERY_KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not BIGQUERY_KEY_PATH:
    raise ValueError("A variável GOOGLE_APPLICATION_CREDENTIALS não está definida no .env")

BIGQUERY_KEY_PATH = BASE_DIR / "clients"/"key.json"

# 2. Define a variável de ambiente para o client do BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(BIGQUERY_KEY_PATH)

# 3. Define o projeto e dataset
BIGQUERY_PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID", "agro-data-476422")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "agro-data")

# ===========================
# Client modularizado do BigQuery
# ===========================
def get_bigquery_client():
    """
    Retorna um client do BigQuery usando o arquivo JSON da service account.
    """
    return bigquery.Client(project=BIGQUERY_PROJECT_ID)

# ===========================
# Teste rápido (opcional)
# ===========================
if DEBUG:
    client = get_bigquery_client()
    print("BigQuery client inicializado para projeto:", BIGQUERY_PROJECT_ID)
