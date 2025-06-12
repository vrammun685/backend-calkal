# settings/__init__.py
# Carga el archivo .env desde la raíz del proyecto

ENV = 'produccion'

if ENV == 'production':
    from .production import *
else:
    print(ENV)
    from .local import *