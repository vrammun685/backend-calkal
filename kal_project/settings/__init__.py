# settings/__init__.py
# Carga el archivo .env desde la raíz del proyecto

from decouple import config
ENV = config('DJANGO_ENV')

if ENV == 'production':
    from .production import *
else:
    print(ENV)
    from .local import *