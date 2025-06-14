from .base import *
import os
import dj_database_url

DEBUG = False

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
STATIC_URL = '/static/'

CORS_ALLOWED_ORIGINS = [
    'https://calkal.netlify.app',  # Permitir solicitudes desde tu frontend React
]
