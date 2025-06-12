from pathlib import Path
from .base import *
import os
from decouple import config
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ['backend-calkal.onrender.com']

ROOT_URLCONF = 'kal_project.urls'

# Cargar credenciales desde .env
print("DATABASE_URL desde .env:", os.getenv("DATABASE_URL"))
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}


CORS_ALLOWED_ORIGINS = [
    'https://calkal.netlify.app',  # Permitir solicitudes desde tu frontend React
]

print("DEBUG:", DEBUG)
print("ALLOWED_HOSTS:", ALLOWED_HOSTS)
print("ROOT_URLCONF:", ROOT_URLCONF)
print("INSTALLED_APPS:", INSTALLED_APPS)