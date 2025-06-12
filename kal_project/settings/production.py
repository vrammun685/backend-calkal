from pathlib import Path
try:
    from .base import *
except Exception as e:
    print("ERROR al importar base.py:", e)
    raise
import os
from decouple import config
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ['backend-calkal.onrender.com']

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
