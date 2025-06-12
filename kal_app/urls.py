from django.urls import path
from .views import *

urlpatterns = [

    #Login y Registros
    path('api/register/', RegistroUsuario.as_view(), name='register'),
    path('api/login/', Login.as_view(), name="login"),
    path('api/solicitar-contraseña/', SolicitarCorreoPass.as_view(), name="SolicitarCorreoPass"),
    path('api/CambiaContraseña/<uidb64>/<token>/', CambiarContraseña.as_view(), name="CambiarContraseña"),
    path("api/logout/", Logout.as_view(), name="logout"),
    path('api/check-username/', CheckUsername.as_view(), name='check-username'),
    path('api/check-email/', CheckEmail.as_view(), name='check-email'),

    #Token
    path('api/checktoken/', CheckToken.as_view(), name="checkToken"),
    path('api/refreshtoken/', Refresh_Token.as_view(), name="refreshToken"),

    #Paginas
    path('api/home/', Home.as_view(), name="Home"),
    path('api/imagenPrefil/', SolicitarImagenPerfil.as_view(), name="Home"),
    path('api/diario/', Diarios.as_view(), name="Diarios"),
    path('api/pesos/', Pesos.as_view(), name='pesos'),
    path('api/pesos/<int:pk>/', Pesos.as_view(), name='pesoseliminar'),
    path('api/perfil/', Perfil.as_view(), name="perfil"),
    path('api/diarios/crearAlimento/', AlimentoConsumidoCrear.as_view(), name='alimentos-list'),
    path('api/diarios/crearReceta/', ComidaConsumidaCrear.as_view(), name='alimentos-list'),
    path('api/diarios/crearAlimento/<int:pk>/', AlimentoConsumidoCrear.as_view(), name='alimentos-list'),
    path('api/diarios/crearReceta/<int:pk>/', ComidaConsumidaCrear.as_view(), name='alimentos-list'),
    path('api/recetas/', Recetas.as_view(), name='alimentos-list'),
    path('api/recetas/<int:pk>/', Recetas.as_view(), name='alimentos-list'),
    path('api/ingredientes/<int:pk>/', IngredientesDeReceta.as_view(), name='alimentos-list'),
    path('api/recetas/crear/', ComidaCreateView.as_view(), name='receta-crear'),
    path('api/recetas/<int:pk>/editar/', ComidaCreateView.as_view(), name='receta-crear'),
  
    #API
    path('api/alimentos/', AlimentoListAPIView.as_view(), name='alimentos-list'),

    #ADMIN
    path('api/paneladmin/usuarios/', admin_panel_usuarios.as_view(), name='admin-panel'),
    path('api/paneladmin/alimentos/', admin_panel_alimentos.as_view(), name='admin-panel'),
    path('api/paneladmin/alimentos/<int:pk>/', admin_panel_alimentos.as_view(), name='admin-panel-eliminar alimento'),
]