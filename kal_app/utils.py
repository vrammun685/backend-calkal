from django.core.mail import send_mail
from django.conf import settings
from .models import Diario, PesoRegistrado, Usuario, ComidaConsumida, AlimentoConsumido
from datetime import date

def mensaje_Almuerzo():
    hoy = date.today()
    usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False, notificaciones=True)
    
    for usuario in usuarios:
        print(usuario.username)
        almuerzo=False
        diario = Diario.objects.filter(usuario=usuario, fecha=hoy).first()
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

                Tómate un momento para anotar lo que has comido en el almuerzo en la sección de "Diario".

                Saludos,  
                El equipo de CalKal.
                """

            emisario = settings.EMAIL_HOST_USER
            listaReceptores = [usuario.email]
            send_mail(asunto, mensaje, emisario, listaReceptores)

def mensaje_Desayuno():
    hoy = date.today()
    usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False, notificaciones=True)
    
    for usuario in usuarios:
        almuerzo=False
        diario = Diario.objects.filter(usuario=usuario, fecha=hoy).first()
        if  AlimentoConsumido.objects.filter(diario=diario, parte_del_dia='Desayuno').exists():
            almuerzo=True
        elif ComidaConsumida.objects.filter(diario=diario, parte_del_dia='Desayuno').exists():
            almuerzo=True        
            
        if not almuerzo:
            asunto = "¡No olvides registrar tu desayuno de hoy 🍽️!"
            mensaje = mensaje = f"""
                Hola {usuario.username},

                Hemos notado que todavía no has registrado tu desayuno en la aplicación hoy.
                Llevar un control diario de tus comidas te ayuda a mantener tus objetivos de salud y bienestar.

                Tómate un momento para anotar lo que has comido en el desayuno en la sección de "Diario".

                Saludos,  
                El equipo de CalKal.
                """

            emisario = settings.EMAIL_HOST_USER
            listaReceptores = [usuario.email]
            send_mail(asunto, mensaje, emisario, listaReceptores)

def mensaje_Cena():
    hoy = date.today()
    usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False, notificaciones=True)
    for usuario in usuarios:
        print(usuario.username)
        almuerzo=False
        diario = Diario.objects.filter(usuario=usuario, fecha=hoy).first()
        if  AlimentoConsumido.objects.filter(diario=diario, parte_del_dia='Cena').exists():
            almuerzo=True
        elif ComidaConsumida.objects.filter(diario=diario, parte_del_dia='Cena').exists():
            almuerzo=True        
            
        if not almuerzo:
            asunto = "¡No olvides registrar tu cena de hoy 🍽️!"
            mensaje = mensaje = f"""
                Hola {usuario.username},

                Hemos notado que todavía no has registrado tu cena en la aplicación hoy.
                Llevar un control diario de tus comidas te ayuda a mantener tus objetivos de salud y bienestar.

                Tómate un momento para anotar lo que has comido en el cena en la sección de "Diario".

                Saludos,  
                El equipo de CalKal.
                """

            emisario = settings.EMAIL_HOST_USER
            listaReceptores = [usuario.email]
            send_mail(asunto, mensaje, emisario, listaReceptores)

def Crear_Diarios_auto():
    hoy = date.today()
    usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False)

    for usuario in usuarios:
        if not Diario.objects.filter(usuario=usuario, fecha=hoy).exists():
            if usuario.peso and usuario.altura and usuario.edad:
                try:
                    crearDiario(usuario)
                    print(f"✅ Creado diario para {usuario.username} en {hoy}")
                except Exception as e:
                    print(f"❌ Error creando diario para {usuario.username}: {e}")
            else:
                print(f"⚠️ Usuario {usuario.username} sin datos completos, omitido.")
        else:
            print(f"ℹ️ Diario ya existente para {usuario.username} en {hoy}")
                
def correo_bienvenida(email, nombre):
    asunto = "Bienvenido a Calkal"
    mensaje = f"Muchisimas gracias {nombre},\n Por confiar en Calkal para tu proceso de cambio fisico"
    emisario = settings.EMAIL_HOST_USER
    listaReceptores = [email]

    send_mail(asunto, mensaje, emisario, listaReceptores)

def correo_cambiar_Contraseña(usuario, uid, token):
    

    link = f'http://localhost:3000/RecuperarContraseña/EscribirContraseña/{uid}/{token}'

    asunto = 'Cambiar Contraseña'
    mensaje = f"""
        Hola {usuario.username},

        Recibimos una solicitud para restablecer tu contraseña.

        Por favor, hacé clic en el siguiente enlace para establecer una nueva contraseña:

        {link}

        Si no fuiste vos, ignorá este correo.

        Saludos,  
        El equipo de CalKal.
        """
    emisario = settings.EMAIL_HOST_USER
    listaReceptores = [usuario.email]

    send_mail(asunto, mensaje, emisario, listaReceptores)

def cambiar_Contraseña(usuario, nueva_Contraseña):
    usuario.set_password(nueva_Contraseña)
    usuario.save()


def crearDiario(user):
    diario = Diario.objects.create(
        usuario=user,  
        calorias_a_Consumir=user.calcular_Calorias(),
        proteinas_a_Consumir=user.calcular_Proteinas(),
        grasas_a_Consumir=user.calcular_Grasas(),
        carbohidratos_a_Consumir=user.calcular_Carbohidratos()
    )
    return diario

def crearPeso(usuario):
    PesoRegistrado.objects.create(
        usuario = usuario,
        peso = usuario.peso
    )

def actualizarTraEditarPeso(usuario, peso):
    usuario.peso = peso
    usuario.save()
    print(type(peso))
    diario = Diario.objects.filter(usuario=usuario).order_by('-fecha').first()
    diario.calorias_a_Consumir= usuario.calcular_Calorias()
    diario.carbohidratos_a_Consumir= usuario.calcular_Carbohidratos()
    diario.proteinas_a_Consumir= usuario.calcular_Proteinas()
    diario.grasas_a_Consumir=usuario.calcular_Grasas()
    print('diario actualizado')
    diario.save()

def actualizarTrasActualizar(usuario):
    diario = Diario.objects.filter(usuario=usuario).order_by('-fecha').first()
    if diario:
        diario.calorias_a_Consumir = usuario.calcular_Calorias()
        diario.carbohidratos_a_Consumir = usuario.calcular_Carbohidratos()
        diario.proteinas_a_Consumir = usuario.calcular_Proteinas()
        diario.grasas_a_Consumir = usuario.calcular_Grasas()
        print('diario actualizado')
        diario.save()
    else:
        print('No existe diario para este usuario, no se pudo actualizar')

def ActualizardiarioPorAlimento(diario):
    alimentos = AlimentoConsumido.objects.filter(diario=diario)
    diario.calorias_Consumidas = sum(a.calorias_totales() for a in alimentos)
    diario.proteinas_Consumidas = sum(a.proteinas_totales() for a in alimentos)
    diario.grasas_Consumidas = sum(a.grasas_totales() for a in alimentos)
    diario.carbohidratos_Consumidas = sum(a.carbohidratos_totales() for a in alimentos)
    diario.save()

def ActualizardiarioPorComida(diario):
    comidas_consumidas = ComidaConsumida.objects.filter(diario=diario)
    
    diario.calorias_Consumidas = sum(c.calorias_totales() for c in comidas_consumidas)
    diario.proteinas_Consumidas = sum(c.proteinas_totales() for c in comidas_consumidas)
    diario.grasas_Consumidas = sum(c.grasas_totales() for c in comidas_consumidas)
    diario.carbohidratos_Consumidas = sum(c.carbohidratos_totales() for c in comidas_consumidas)
    
    diario.save()
