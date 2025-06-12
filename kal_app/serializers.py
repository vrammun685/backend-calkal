from rest_framework import serializers
from .models import *

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'altura', 'edad', 'peso', 'genero', 'objetivo', 'actividad',
            'imagen_Perfil', 'notificaciones', 'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso")
        return value
        
    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado")
        return value

    def create(self, validated_data):
        imagen = validated_data.pop('imagen_Perfil', None)
        user = Usuario.objects.create_user(**validated_data)
        if imagen:
            user.imagen_Perfil = imagen
            user.save()
        return user

class UsuarioEditarPerfilSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    imagen_Perfil = serializers.SerializerMethodField()
    class Meta:
        model = Usuario
        fields = ['username', 'email','first_name', 'last_name', 'peso', 'altura', 'edad', 'genero', 'objetivo', 'actividad','notificaciones', 'imagen_Perfil']

    def get_imagen_Perfil(self, obj):
        request = self.context.get('request')
        if obj.imagen_Perfil and hasattr(obj.imagen_Perfil, 'url'):
            return request.build_absolute_uri(obj.imagen_Perfil.url)
        return None

class LoginSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PesoRegistradoSerializer(serializers.ModelSerializer):
    foto_pesaje = serializers.SerializerMethodField()

    class Meta:
        model = PesoRegistrado
        fields = ['id', 'peso', 'fecha', 'foto_pesaje', 'usuario']

    def get_foto_pesaje(self, obj):
        request = self.context.get('request')
        if obj.foto_pesaje and hasattr(obj.foto_pesaje, 'url'):
            return request.build_absolute_uri(obj.foto_pesaje.url) if request else obj.foto_pesaje.url
        return None

class DiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diario
        fields = [
            'id', 'usuario','fecha', 'calorias_Consumidas', 'calorias_a_Consumir', 'proteinas_Consumidas', 'proteinas_a_Consumir', 'grasas_Consumidas', 'grasas_a_Consumir', 'carbohidratos_Consumidas', 'carbohidratos_a_Consumir',
        ]

class ComidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comida
        fields = '__all__'

class AlimentoComidaSerializer(serializers.ModelSerializer):
    nombre_es = serializers.CharField(source='alimento.nombre_es')
    nombre_en = serializers.CharField(source='alimento.nombre_en')
    medida = serializers.CharField(source='alimento.medida')
    calorias_totales = serializers.SerializerMethodField()
    grasas_totales = serializers.SerializerMethodField()
    proteinas_totales = serializers.SerializerMethodField()
    carbohidratos_totales = serializers.SerializerMethodField()

    class Meta:
        model = AlimentoComida
        fields = ['nombre_es','nombre_en', 'cantidad', 'medida',
                  'calorias_totales', 'grasas_totales',
                  'proteinas_totales', 'carbohidratos_totales']

    def get_calorias_totales(self, obj):
        return obj.calorias_totales()

    def get_grasas_totales(self, obj):
        return obj.grasas_totales()

    def get_proteinas_totales(self, obj):
        return obj.proteinas_totales()

    def get_carbohidratos_totales(self, obj):
        return obj.carbohidratos_totales()

class AlimentoConsumidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlimentoConsumido
        fields = [
            'id', 'diario', 'cantidad', 'nombre_es', 'nombre_en', 
            'medida', 'grasas', 'proteinas', 'carbohidratos', 
            'codigoAlimentos', 'calorias'
        ]

class AlimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        fields = '__all__'

from rest_framework import serializers
from .models import Comida, AlimentoComida, Alimento

class IngredienteInputSerializer(serializers.Serializer):
    alimento_id = serializers.IntegerField()
    cantidad = serializers.FloatField()

class ComidaCreateSerializer(serializers.ModelSerializer):
    ingredientes = IngredienteInputSerializer(many=True)

    class Meta:
        model = Comida
        fields = ['nombre', 'numeroPorciones', 'ingredientes']
    

    def create(self, validated_data):
        ingredientes_data = validated_data.pop('ingredientes')
        usuario = self.context['request'].user

        comida = Comida.objects.create(
            usuario=usuario,
            nombre=validated_data['nombre'],
            numeroPorciones=validated_data['numeroPorciones'],
            calorias=0, proteinas=0, grasas=0, carbohidratos=0
        )

        total_cal = total_prot = total_grasas = total_carb = 0

        for item in ingredientes_data:
            alimento = Alimento.objects.get(pk=item['alimento_id'])
            cantidad = item['cantidad']

            ingrediente = AlimentoComida.objects.create(
                comida=comida,
                alimento=alimento,
                cantidad=cantidad
            )

            total_cal += ingrediente.calorias_totales()
            total_prot += ingrediente.proteinas_totales()
            total_grasas += ingrediente.grasas_totales()
            total_carb += ingrediente.carbohidratos_totales()

        comida.calorias = total_cal
        comida.proteinas = total_prot
        comida.grasas = total_grasas
        comida.carbohidratos = total_carb
        comida.save()

        return comida

class IngredienteOutputSerializer(serializers.ModelSerializer):
    alimento_id = serializers.IntegerField(source='alimento.id', read_only=True)
    alimento = AlimentoSerializer(read_only=True)  # Tu serializer del alimento, asegúrate de que incluye el id

    class Meta:
        model = AlimentoComida
        fields = ['alimento_id', 'cantidad', 'alimento']

class ComidaEditarSerializer(serializers.ModelSerializer):
    ingredientes = serializers.SerializerMethodField()

    class Meta:
        model = Comida
        fields = ['nombre', 'numeroPorciones', 'ingredientes']

    def get_ingredientes(self, obj):
        ingredientes = obj.alimentos.all()  # o como se llame tu related_name
        return IngredienteOutputSerializer(ingredientes, many=True).data

class AlimentoConsumidoDetalleSerializer(serializers.ModelSerializer):
    nombre_es = serializers.CharField(source='alimento.nombre_es')
    nombre_en = serializers.CharField(source='alimento.nombre_en')
    medida = serializers.CharField(source='alimento.medida')
    calorias = serializers.SerializerMethodField()
    grasas = serializers.SerializerMethodField()
    proteinas = serializers.SerializerMethodField()
    carbohidratos = serializers.SerializerMethodField()

    class Meta:
        model = AlimentoConsumido
        fields = [
            'id', 'nombre_es', 'nombre_en', 'cantidad', 'medida',
            'calorias', 'grasas', 'proteinas', 'carbohidratos',
        ]

    def get_calorias(self, obj):
        return obj.calorias_totales()

    def get_grasas(self, obj):
        return obj.grasas_totales()

    def get_proteinas(self, obj):
        return obj.proteinas_totales()

    def get_carbohidratos(self, obj):
        return obj.carbohidratos_totales()

class ComidaConsumidaDetalleSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='comida.nombre')
    porcion = serializers.FloatField(source='porcion_a_comer')  # ← Esto va FUERA de Meta
    calorias = serializers.SerializerMethodField()
    grasas = serializers.SerializerMethodField()
    proteinas = serializers.SerializerMethodField()
    carbohidratos = serializers.SerializerMethodField()

    class Meta:
        model = ComidaConsumida
        fields = [
            'id', 'nombre', 'porcion', 'calorias',
            'grasas', 'proteinas', 'carbohidratos',
        ]

    def get_calorias(self, obj):
        return obj.calorias_totales()

    def get_grasas(self, obj):
        return obj.grasas_totales()

    def get_proteinas(self, obj):
        return obj.proteinas_totales()

    def get_carbohidratos(self, obj):
        return obj.carbohidratos_totales()

