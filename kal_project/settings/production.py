from pathlib import Path
from .base import *
import os
from decouple import config
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Cargar credenciales desde .env
print("DATABASE_URL desde .env:", os.getenv("DATABASE_URL"))
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

MEDIA_ROOT = BASE_DIR / 'media'