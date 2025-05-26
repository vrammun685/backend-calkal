from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from kal_app.models import Diario,Usuario,AlimentoConsumido, ComidaConsumida
from datetime import date
from django.conf import settings

class Command(BaseCommand):
    help = "Enviar mensaje de que no han añadido nada para el almuerzo"

    def handle(self, *args, **kwargs):

        
        hoy = date.today()
        usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False, notificaciones=True)
        

        for usuario in usuarios:
            almuerzo=False
            diario = Diario.objects.filter(usuario=usuario, fecha=hoy)
            if  AlimentoConsumido.objects.filter(diario=diario, parte_del_dia='Almuerzo').exists():
                almuerzo=True
            elif ComidaConsumida.objects.filter(diario=diario, parte_del_dia='Almuerzo').exists():
                almuerzo=True
            
            if not almuerzo:
                asunto = "¡No olvides registrar tu almuerzo de hoy 🍽️!"
                mensaje = mensaje = f"""
                    Hola {usuario.username},

                    Hemos notado que todavía no has registrado tu almuerzo en la aplicación hoy.
                    Llevar un control diario de tus comidas te ayuda a mantener tus objetivos de salud y bienestar.

                    Tómate un momento para anotar lo que has comido en el Almuerzo en la sección de "Diario".

                    Saludos,  
                    El equipo de CalKal.
                    """

                emisario = settings.EMAIL_HOST_USER
                listaReceptores = [usuario.email]
                send_mail(asunto, mensaje, emisario, listaReceptores)
