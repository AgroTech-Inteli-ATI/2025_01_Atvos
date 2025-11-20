import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.contenttypes', 
    'django.contrib.staticfiles',  
    'rest_framework',
    'corsheaders',
    'django_filters',
    'km_track_api', 
    'travels',
    'dashboard',
    'users'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

BIGQUERY_REQUIRED_VARS = {
    'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    'PROJECT_ID': os.getenv('PROJECT_ID', 'agro-data-476422'),
    'BIGQUERY_DATASET': os.getenv('BIGQUERY_DATASET', 'agro_dataset'),
}

import logging
logger = logging.getLogger(__name__)

for var_name, var_value in BIGQUERY_REQUIRED_VARS.items():
    if not var_value:
        logger.warning(f"⚠️  {var_name} não configurado!")
    else:
        if var_name == 'GOOGLE_APPLICATION_CREDENTIALS':
            logger.info(f"✓ {var_name}: {var_value[:50]}...")
        else:
            logger.info(f"✓ {var_name}: {var_value}")

BIGQUERY_CONFIG = {
    'PROJECT_ID': os.getenv('PROJECT_ID', 'agro-data-476422'),
    'DATASET_ID': os.getenv('BIGQUERY_DATASET', 'agro_dataset'),
    'LOCATION': os.getenv('BIGQUERY_LOCATION', 'us-central1'),
    'CREDENTIALS_PATH': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    'MAX_RESULTS': 10000,
    'QUERY_TIMEOUT': 30,
    'ENABLE_QUERY_CACHE': True,
    'REQUIRE_PARTITION_FILTER': True,
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]

REST_FRAMEWORK = {
    'UNAUTHENTICATED_USER': None,
    'UNAUTHENTICATED_TOKEN': None,
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'bigquery.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'travels.bigquery_manager': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'google.cloud.bigquery': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

(BASE_DIR / 'logs').mkdir(exist_ok=True)