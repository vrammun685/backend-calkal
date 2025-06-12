from .base import *
import os
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Permitir solicitudes desde tu frontend React
]