Semana 3
Creacion del proyecto y aprendizaje de las nuevas tecnologias
Creacion del modelo

Semana 4
Primeras plantillas en react y correcion de errores del modelo. Separacion del backend en local y produccion aunque produccion no tenga todavia nada.
Primeras peticiones al servidor aunque con datos creados por el admin
Filtro para alimentos.
Dibujo de funcionalidad para las UI
Inicio del diseno de las paginas una por una y su logica correspondiente
Inicio del diseno de las paginas de login y registro de usuarios

Semana 5
Registro
------Terminado
Creacion de usuarios y manejo de validaciones a la hora de enviar los datos
------Por hacer
Manejo de errores en el backend para visualizarlos tanto en ingles como en espanol

Login
------Terminado
Recoger formulario y envio del token
------Por hacer
Autenticacion por token.
Mostrar mensaje de error de autenticacion

Semana 6
--Recuperar contrasena
--Autenticacion por token guardado en el localstorage(Cambiar a una cookie httpOnly) --> Leer Errores de en recuperacion de contrasenas en ChatGPT
--Logica del home
--tokens, 


Fallos Detectados
--Cuando un token caduca e intentas acceder al otra pagina no carga los datos por que no hace refreshtoken

Que meter en la Presentacion
--Meter en la presentacion animaciones de inicio
--Cambie el video de fondo
--Cambiar Fuente


Paleta de Colores
Color Principal ---> #4CAF87
Color Secundario ---> #E4B363
Fondo ----> #E8E9EB
Letra ---> #313638
Errores ----> #EF6461

Que quiero que haga la pagina de Diaros quiero 5 desplegables donde veas las 3 comidas, los aperitivos y el ejercicio que haya si no hay pues nos jodimos y decimos que no hay alimento anadido todavia. Un panel para editar u poco mas 

Para diarios necesito llevarme todos los alimentosCondumidos y comidas por diario 

https://bentogrids.com/shots/cltgwuq2s0002p3kvfireey42 para pesos

0 2 * * * cd /ruta/a/carpetax && /ruta/a/carpetax/venv/bin/python manage.py crear_diarios --settings=mi_proyecto.settings.base >> logs/crear_diarios.log 2>&1 comando para cron en produccion necesito un sitio que tenga terminal para ejecutar esto

Cosas que debo de cambiar para produccuion en el backend
link para produccion del correo del cambiar contrasena
La url de la base de datos, debo usar la interna vale
samesite='None',  # MUY IMPORTANTE si los dominios son distintos
secure=True       # Obligatorio si samesite es None

Pasar el # SECURITY WARNING: keep the secret key used in production secret! al env de render
SECRET_KEY = 'django-insecure-x4@bh_p_!*qr5x2(!*9%9!zmkl1p)ujaqei2^rn=!-2y9&_47='

poner esto login
secure_cookie = not settings.DEBUG
samesite_policy = 'None' if not settings.DEBUG else 'Lax'

Para login y refresh_token
response.set_cookie(
    key='token',
    value=access_token,
    httponly=True,
    secure=secure_cookie,
    max_age=3600,
    samesite=samesite_policy,
)

response.set_cookie(
    key='refresh_token',
    value=refresh_token,
    httponly=True,
    secure=secure_cookie,
    max_age=7 * 24 * 60 * 60,
    samesite=samesite_policy,
)

externa
DATABASE_URL=postgresql://calkal_user:krz87EQu29ZtYpkHlYkED0D90Qylk9oD@dpg-d0q55iodl3ps73bb41rg-a.frankfurt-postgres.render.com:5432/calkaldb

interna
DATABASE_URL=postgresql://calkal_user:krz87EQu29ZtYpkHlYkED0D90Qylk9oD@dpg-d0q55iodl3ps73bb41rg-a5432/calkaldb

actualizar al anadir alimentos.
crear recetas
eliminar alimentos

Poner mensaje contrasenia