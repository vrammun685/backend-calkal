from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AlimentoComida, AlimentoConsumido, Comida, Usuario, Diario, PesoRegistrado, Alimento, ComidaConsumida

# Register your models here.
class UsuarioAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
         (None, {'fields': ('altura', 'edad', 'peso','genero', 'objetivo', 'actividad','imagen_Perfil', 'notificaciones')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
         (None, {'fields': ('altura', 'edad', 'peso', 'genero', 'objetivo', 'actividad', 'imagen_Perfil', 'notificaciones')}),
    )

admin.site.register(AlimentoComida),
admin.site.register(AlimentoConsumido),
admin.site.register(Comida),
admin.site.register(Usuario, UsuarioAdmin),
admin.site.register(Diario),
admin.site.register(PesoRegistrado),
admin.site.register(Alimento),
admin.site.register(ComidaConsumida),
