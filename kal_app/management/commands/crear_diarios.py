from django.core.management.base import BaseCommand
from datetime import date
from django.contrib.auth.models import User
from kal_app.models import Diario,Usuario  # Ajusta si está en otra app
from kal_app.utils import crearDiario

class Command(BaseCommand):
    help = "Crear diarios para todos los usuarios para el día actual"

    def handle(self, *args, **kwargs):
        hoy = date.today()
        usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False)

        for usuario in usuarios:
            if not Diario.objects.filter(usuario=usuario, fecha=hoy).exists():
                if usuario.peso and usuario.altura and usuario.edad:
                    try:
                        crearDiario(usuario)
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ Creado diario para {usuario.username} en {hoy}"
                        ))
                    except Exception as e:
                        self.stderr.write(f"❌ Error creando diario para {usuario.username}: {e}")
                else:
                    self.stdout.write(f"⚠️ Usuario {usuario.username} sin datos completos, omitido.")
            else:
                self.stdout.write(f"ℹ️ Diario ya existente para {usuario.username} en {hoy}")