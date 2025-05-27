# settings/__init__.py
# Carga el archivo .env desde la raíz del proyecto

ENV = 'production'

if ENV == 'production':
    print(ENV)
    from .production import *
else:
    print(ENV)
    from .local import *