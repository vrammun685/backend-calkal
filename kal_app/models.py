from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
import math
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

class Usuario(AbstractUser):
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    GENEROS = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]

    OBJETIVOS = [
        ('Perder peso', 'Perder peso'),
        ('Mantener peso', 'Mantener peso'),
        ('Ganar peso', 'Ganar peso'),
    ]    
    ACTIVIDAD = [
        ('Nula', 'Nula'),
        ('1 a 2 veces en semana', '1 a 2 veces en semana'),
        ('3 a 5 veces en semana', '3 a 5 veces en semana'),
        ('6 a 7 veces en semana', '6 a 7 veces en semana'),
        ('Ejercicio intenso a diario', 'Ejercicio intenso a diario'),
    ]

    altura = models.FloatField(null=True, blank=True)
    edad = models.IntegerField(validators=[MinValueValidator(12)], null=True, blank=True)
    peso = models.FloatField(null=True, blank=True)
    imagen_Perfil = CloudinaryField('imagen_Perfil', null=True, blank=True)
    genero = models.CharField(max_length=100, choices=GENEROS, default='Selecciona biologicamente', null=True, blank=True)
    objetivo = models.CharField(max_length=200, choices=OBJETIVOS, default='Selecciona una opcion', null=True, blank=True)
    actividad = models.CharField(max_length=30, choices=ACTIVIDAD, default='Selecciona una opcion', null=True, blank=True)
    notificaciones = models.BooleanField(default=True)

    def __str__(self):
        return self.first_name
    
    def calcular_Calorias(self):
        if(self.genero == "Masculino"):
            tmb = 5 + (10*self.peso)+(6.25*self.altura)-(5*self.edad)
        else:
            tmb =(10*self.peso)+(6.25*self.altura)-(5*self.edad) -161
        
        if(self.actividad == 'Nula'):
            calorias_mantenimiento = tmb*1.2
        elif(self.actividad == '1 a 2 veces en semana'):
            calorias_mantenimiento = tmb*1.375
        elif(self.actividad == '3 a 5 veces en semana'):
            calorias_mantenimiento = tmb*1.55
        elif(self.actividad == '6 a 7 veces en semana'):
            calorias_mantenimiento = tmb*1.725
        else:
            calorias_mantenimiento = tmb*1.9

        if(self.objetivo == 'Perder peso'):
            calorias = calorias_mantenimiento - 400
        elif(self.objetivo == 'Ganar peso'):
            calorias = calorias_mantenimiento + 400
        else:
            calorias = calorias_mantenimiento   
        
        return math.ceil(calorias)
    
    def calcular_Proteinas(self):
        if not self.peso or not self.objetivo:
            return None

        if self.objetivo == 'Perder peso':
            gramos_por_kg = 2.0  # un rango alto para preservar músculo
        elif self.objetivo == 'Ganar peso':
            gramos_por_kg = 1.6  # suficiente para hipertrofia
        else:
            gramos_por_kg = 1.2  # mantenimiento

        proteinas = self.peso * gramos_por_kg
        return round(proteinas, 1)
    
    def calcular_Grasas(self):
        if not self.peso or not self.objetivo:
            return None

        # Gramos por kg de grasa, aproximados
        if self.objetivo == 'Perder peso':
            gramos_por_kg = 0.8
        elif self.objetivo == 'Ganar peso':
            gramos_por_kg = 1.0
        else:
            gramos_por_kg = 0.9

        grasas = self.peso * gramos_por_kg
        return round(grasas, 1)


    def calcular_Carbohidratos(self):
        if not self.peso or not self.objetivo:
            return None

        # Gramos por kg de carbohidratos, aproximados
        if self.objetivo == 'Perder peso':
            gramos_por_kg = 2.5
        elif self.objetivo == 'Ganar peso':
            gramos_por_kg = 4.0
        else:
            gramos_por_kg = 3.0

        carbohidratos = self.peso * gramos_por_kg
        return round(carbohidratos, 1)
    
    groups = models.ManyToManyField(
        Group,
        related_name='usuario_set',  # <-- evita el conflicto
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuario_perms_set',  # <-- evita el conflicto
        blank=True
    )


class PesoRegistrado(models.Model):
    class Meta:
        verbose_name = 'Pesos Registrados'
        verbose_name_plural = 'Lista de Pesos registrados'

    peso = models.FloatField()
    fecha = models.DateField(default=timezone.now)
    foto_pesaje = CloudinaryField('foto_pesaje', null=True, blank=True,)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pesos')

    def __str__(self):
        return f"{self.usuario.username} - {self.peso} kg - {self.fecha.strftime('%Y-%m-%d %H:%M')}"


class Diario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='diarios')
    fecha = models.DateField(auto_now_add=True)

    #Calorias
    calorias_Consumidas = models.FloatField(default=0, null=True, blank=True)
    calorias_a_Consumir = models.FloatField(default=0, null=True, blank=True)

    #Proteinas
    proteinas_Consumidas = models.FloatField(default=0, null=True, blank=True)
    proteinas_a_Consumir = models.FloatField(default=0, null=True, blank=True)

    #Grasas
    grasas_Consumidas = models.FloatField(default=0, null=True, blank=True)
    grasas_a_Consumir = models.FloatField(default=0, null=True, blank=True)

    #Carbohidratos
    carbohidratos_Consumidas = models.FloatField(default=0, null=True, blank=True)
    carbohidratos_a_Consumir = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        verbose_name = 'Diario'
        verbose_name_plural = 'Diarios'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"

class Alimento(models.Model):
    MEDIDAS = [
        ('g', 'Gramos'),
        ('ml', 'Mililitros')
        # Puedes agregar más según lo que manejes
    ]

    codigo = models.CharField(max_length=10, unique=True)
    nombre_es = models.CharField(max_length=50)
    nombre_en = models.CharField(max_length=50)
    calorias = models.FloatField()
    grasas = models.FloatField()
    proteinas = models.FloatField()
    carbohidratos = models.FloatField()
    medida = models.CharField(max_length=20, choices=MEDIDAS, default='g')

    class Meta:
        verbose_name = 'Alimento'
        verbose_name_plural = 'Alimentos'

    def __str__(self):
        return f"{self.nombre_es} ({self.codigo})"

class Comida(models.Model):
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comidas')   
    nombre = models.CharField(max_length=20)
    numeroPorciones = models.FloatField(default=1)
    calorias = models.FloatField() 
    proteinas = models.FloatField()
    grasas = models.FloatField()
    carbohidratos = models.FloatField()


    class Meta:
        verbose_name = 'Comida'
        verbose_name_plural = 'Comidas'

class ComidaConsumida(models.Model):
    PARTE_DIA =[
        ('Desayuno', 'Desayuno'),
        ('Almuerzo', 'Almuerzo'),
        ('Cena', 'Cena'),
        ('Otro', 'Otro')
    ]

    parte_del_dia=models.CharField(max_length=30, choices=PARTE_DIA, default='Selecciona una opcion')
    diario = models.ForeignKey(Diario, on_delete=models.CASCADE, related_name='comidas',)
    comida= models.ForeignKey(Comida, on_delete=models.CASCADE)
    porcion_a_comer= models.FloatField()

    def calorias_totales(self):
        return (self.comida.calorias * self.porcion_a_comer) / self.comida.numeroPorciones  # Asumiendo 100g como referencia

    def grasas_totales(self):
        return (self.comida.grasas * self.porcion_a_comer) / self.comida.numeroPorciones

    def proteinas_totales(self):
        return (self.comida.proteinas * self.porcion_a_comer) / self.comida.numeroPorciones

    def carbohidratos_totales(self):
        return (self.comida.carbohidratos * self.porcion_a_comer) / self.comida.numeroPorciones


class AlimentoComida(models.Model):
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE, related_name='alimentos')
    alimento = models.ForeignKey(Alimento, on_delete=models.PROTECT)  # ← Referencia al alimento base
    cantidad = models.FloatField()  # Cantidad usada en la comida

    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'

    def __str__(self):
        return f"{self.alimento.nombre_es} - {self.cantidad}{self.alimento.medida}"

    def calorias_totales(self):
        return (self.cantidad * self.alimento.calorias) / 100  # Asumiendo 100g como referencia

    def grasas_totales(self):
        return (self.cantidad * self.alimento.grasas) / 100

    def proteinas_totales(self):
        return (self.cantidad * self.alimento.proteinas) / 100

    def carbohidratos_totales(self):
        return (self.cantidad * self.alimento.carbohidratos) / 100


class AlimentoConsumido(models.Model):
    PARTE_DIA = [
        ('Desayuno', 'Desayuno'),
        ('Almuerzo', 'Almuerzo'),
        ('Cena', 'Cena'),
        ('Otro', 'Otro')
    ]

    diario = models.ForeignKey(Diario, on_delete=models.CASCADE, related_name='alimentos_consumidos')
    alimento = models.ForeignKey(Alimento, on_delete=models.PROTECT)  # ← Enlace al alimento base
    parte_del_dia = models.CharField(max_length=30, choices=PARTE_DIA, default='Otro')
    cantidad = models.FloatField()  # Esto representa la cantidad consumida

    class Meta:
        verbose_name = 'Alimento Consumido'
        verbose_name_plural = 'Alimentos Consumidos'

    def __str__(self):
        return f"{self.alimento.nombre_es} - {self.cantidad}{self.alimento.medida} ({self.parte_del_dia})"

    def calorias_totales(self):
        return (self.cantidad * self.alimento.calorias) / 100 
    
    def grasas_totales(self):
        return (self.cantidad * self.alimento.grasas) / 100

    def proteinas_totales(self):
        return (self.cantidad * self.alimento.proteinas) / 100

    def carbohidratos_totales(self):
        return (self.cantidad * self.alimento.carbohidratos) / 100


