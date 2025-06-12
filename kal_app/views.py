from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from kal_project import settings
from .models import Usuario, Diario, PesoRegistrado, AlimentoConsumido, Comida, Alimento
from .serializers import *
from .utils import correo_bienvenida, correo_cambiar_Contraseña, cambiar_Contraseña, crearDiario, crearPeso, actualizarTrasActualizar, actualizarTraEditarPeso, ActualizardiarioPorComida, ActualizardiarioPorAlimento
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import AuthenticationFailed
from datetime import date
from collections import defaultdict
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.
    
class AlimentoListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Alimento.objects.all()
    serializer_class = AlimentoSerializer
    renderer_classes = [JSONRenderer]

class CheckUsername(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if username is None:
            return Response({"error": "No username provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        exists = Usuario.objects.filter(username=username).exists()
        return Response({"exists": exists})

class CheckEmail(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        if email is None:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        exists = Usuario.objects.filter(email=email).exists()
        return Response({"exists": exists})
    
class RegistroUsuario(CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        user = serializer.save()
        crearDiario(user)
        crearPeso(user)
        correo_bienvenida(user.email, user.first_name)

class Login(APIView):
    def post(self, request):
        # Validamos los datos del formulario
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            password = serializer.validated_data['password']

            # Intentamos autenticar al usuario con nombre de usuario o email
            user = authenticate(request, username=usuario, password=password)
            if user is None:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            #Creamos el diario del dia
            if not user.is_staff:
                diario = Diario.objects.filter(usuario=user).order_by('-fecha').first()
                if not diario or diario.fecha != date.today():
                    diario = crearDiario(user)

            # Si la autenticación es exitosa, creamos un token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Enviamos el token al frontend
            response = Response({
                "message":"Login successful",
                "is_admin": user.is_staff,
            })
            secure_cookie = not settings.DEBUG
            samesite_policy = 'None' if not settings.DEBUG else 'Lax'

            response.set_cookie(
                key='token',
                value=access_token,
                httponly=True,
                secure=True,
                max_age=3600,
                samesite='None',
            )

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                max_age=7 * 24 * 60 * 60,
                samesite='None',
            )
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckToken(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            return Response({"message": "Token válido"})
        except AuthenticationFailed:
            return Response({"error": "Token no válido o ha expirado, por favor inicie sesión nuevamente."}, status=status.HTTP_401_UNAUTHORIZED)

class Refresh_Token(APIView):
    def post(self, request):
        # Obtener el refresh_token de las cookies
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({"error": "No se proporcionó refresh token."}, status=400)

        try:
            # Validamos el refresh_token
            refresh = RefreshToken(refresh_token)
            # Recuperamos el usuario usando el 'user_id' en el payload del refresh token
            user = Usuario.objects.get(id=refresh.payload['user_id'])

            # Generamos un nuevo access_token
            new_access_token = str(refresh.access_token)

            # Devolvemos el nuevo access token
            response = Response({
                "access_token": new_access_token
            })
            # Almacenamos el nuevo access token en la cookie
            secure_cookie = not settings.DEBUG
            samesite_policy = 'None' if not settings.DEBUG else 'Lax'

            response.set_cookie(
                key='token',
                value=new_access_token,
                httponly=True,
                secure=True,
                max_age=3600,
                samesite='None',
            )
            return response

        except Exception as e:
            # Si algo falla (token inválido, no encontrado, etc.)
            raise AuthenticationFailed('El refresh token no es válido o ha expirado.')
        
class Logout(APIView):
    def post(self, request):
        response = Response({"message":"Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie('token')
        response.delete_cookie('refresh_token')
        return response

class SolicitarCorreoPass(APIView):
    def post(self, request):
        email_selec=request.data.get('email')
        usuario = Usuario.objects.filter(email=email_selec).first()
        if usuario:
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            correo_cambiar_Contraseña(usuario, uid, token)
            return Response({"message": "Correo enviado."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No registrado."}, status=status.HTTP_400_BAD_REQUEST)

class CambiarContraseña(APIView):
    def post(self, request, uidb64, token):
        nueva_Contraseña = request.data.get('password')
        #Decodificar el usuario (UID)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            usuario = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            return Response({'error': 'Usuario no válido'}, status=status.HTTP_400_BAD_REQUEST)
        
        #Verificar el token
        if default_token_generator.check_token(usuario, token):
            cambiar_Contraseña(usuario , nueva_Contraseña)

            return Response({'message': 'Contraseña cambiada correctamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Token inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)

class SolicitarImagenPerfil(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user

        if usuario.imagen_Perfil:
            # Si estás usando Cloudinary, imagen_Perfil.url ya es una URL absoluta
            imagen_url = usuario.imagen_Perfil.url
        else:
            imagen_url = None

        return Response({"foto_perfil": imagen_url})

class Home(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        diario = Diario.objects.filter(usuario=usuario).order_by('-fecha').first()
        diario_serializado = DiarioSerializer(diario)
        return Response({"diario": diario_serializado.data,})

class Diarios(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        diarios = Diario.objects.filter(usuario=usuario).order_by('-fecha')[:5]

        if not diarios:
            return Response({"detalle": "No hay diarios."}, status=404)

        resultado = []

        for diario in diarios:
            # Agrupar alimentos consumidos
            alimentos = AlimentoConsumido.objects.filter(diario=diario)
            alimentos_agrupados = defaultdict(list)
            for a in alimentos:
                data = AlimentoConsumidoDetalleSerializer(a).data
                alimentos_agrupados[a.parte_del_dia.lower()].append(data)

            # Agrupar comidas
            comidas = ComidaConsumida.objects.filter(diario=diario)
            comidas_agrupadas = defaultdict(list)
            for c in comidas:
                data = ComidaConsumidaDetalleSerializer(c).data
                comidas_agrupadas[c.parte_del_dia.lower()].append(data)

            resultado.append({
                "fecha": diario.fecha,
                "alimentos": alimentos_agrupados,
                "comidas": comidas_agrupadas,
            })

        return Response({
            "diarios": resultado
        })

class AlimentoConsumidoCrear(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user
        diario = Diario.objects.filter(usuario=usuario).order_by('-fecha').first()
        if not diario:
            return Response({"error": "No diario found for user."}, status=status.HTTP_400_BAD_REQUEST)

        alimento_id = request.data.get('alimento')
        cantidad = request.data.get('cantidad')
        parte_dia = request.data.get('parte_dia')

        # Validaciones básicas
        if not alimento_id or not cantidad or not parte_dia:
            return Response({"error": "Faltan datos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            alimento = Alimento.objects.get(id=alimento_id)
        except Alimento.DoesNotExist:
            return Response({"error": "Alimento no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Crear el objeto manualmente
        alimento_consumido = AlimentoConsumido.objects.create(
            alimento=alimento,
            cantidad=cantidad,
            parte_del_dia=parte_dia,
            diario=diario
        )
        ActualizardiarioPorAlimento(diario)
        # Puedes devolver los datos que quieras
        return Response(status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk):
        try:
            alimento = AlimentoConsumido.objects.get(pk=pk, diario__usuario=request.user)
        except AlimentoConsumido.DoesNotExist:
            return Response({"detalle": "Alimento no encontrado o no tienes permiso"}, status=status.HTTP_404_NOT_FOUND)

        alimento.delete()
        diario = Diario.objects.filter(usuario=request.user).order_by('-fecha').first()
        ActualizardiarioPorAlimento(diario)
        return Response({"detalle": "Alimento eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)

class ComidaConsumidaCrear(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user

        diario = Diario.objects.filter(usuario=usuario).order_by('-fecha').first()
        if not diario:
            return Response({"error": "No se encontró un diario para este usuario."}, status=status.HTTP_400_BAD_REQUEST)

        comida_id = request.data.get('comida')
        porcion_a_comer = request.data.get('porcion_a_comer')
        parte_dia = request.data.get('parte_del_dia')

        if not comida_id or not porcion_a_comer or not parte_dia:
            return Response({"error": "Faltan datos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comida = Comida.objects.get(id=comida_id)
        except Comida.DoesNotExist:
            return Response({"error": "Comida no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            porcion_a_comer = float(porcion_a_comer)
        except ValueError:
            return Response({"error": "La porción debe ser un número."}, status=status.HTTP_400_BAD_REQUEST)

        comida_consumida = ComidaConsumida.objects.create(
            comida=comida,
            porcion_a_comer=porcion_a_comer,
            parte_del_dia=parte_dia,
            diario=diario
        )

        ActualizardiarioPorComida(diario)

        return Response({"mensaje": "Comida añadida correctamente."}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk):
        try:
            comida = ComidaConsumida.objects.get(pk=pk, diario__usuario=request.user)
        except ComidaConsumida.DoesNotExist:
            return Response({"detalle": "Comida no encontrada o no tienes permiso"}, status=status.HTTP_404_NOT_FOUND)
        comida.delete()
        diario = Diario.objects.filter(usuario=request.user).order_by('-fecha').first()
        ActualizardiarioPorComida(diario)
        return Response({"detalle": "Comida eliminada correctamente"}, status=status.HTTP_204_NO_CONTENT)

class Pesos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        pk = request.GET.get('pk')

        if pk:
            try:
                peso = PesoRegistrado.objects.get(pk=pk, usuario=usuario)
                serializer = PesoRegistradoSerializer(peso, context={'request': request})
                print("pesos GET desde 1 solo")
                return Response(serializer.data)
            except PesoRegistrado.DoesNotExist:
                return Response({'error': 'Peso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        pesos = PesoRegistrado.objects.filter(usuario=usuario)
        serializer = PesoRegistradoSerializer(pesos, many=True, context={'request': request})
        print("pesos GET desde todos")
        return Response({"pesos": serializer.data})
    
    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            peso = PesoRegistrado.objects.get(pk=pk, usuario=self.request.user)
            peso.delete()
            nuevo_peso_valido = PesoRegistrado.objects.filter(usuario=self.request.user).order_by('-fecha').first()
            peso_valor = nuevo_peso_valido.peso
            actualizarTraEditarPeso(self.request.user, peso_valor)
            return Response({'mensaje':'Peso eliminado'}, status=status.HTTP_204_NO_CONTENT)
        except PesoRegistrado.DoesNotExist:
            return Response({'error':'Peso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        usuario = request.user
        fecha = request.data.get('fecha')
        peso_valor = request.data.get('peso')
        imagen = request.FILES.get('imagen')

        if not fecha or not peso_valor:
            return Response({'error': 'Datos incompletos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            peso_valor = float(peso_valor)
        except (TypeError, ValueError):
            return Response({'error': 'Peso inválido, debe ser un número'}, status=status.HTTP_400_BAD_REQUEST)

        peso = PesoRegistrado.objects.create(fecha=fecha, peso=peso_valor, foto_pesaje=imagen, usuario=usuario)
        actualizarTraEditarPeso(usuario, peso_valor)
        return Response({'mensaje': 'Peso creado correctamente', 'id': peso.id}, status=status.HTTP_201_CREATED)

    
    def put(self, request, pk=None):
        if not pk:
            return Response({'error': 'Se requiere la PK del peso a editar'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            peso = PesoRegistrado.objects.get(pk=pk, usuario=request.user)
        except PesoRegistrado.DoesNotExist:
            return Response({'error': 'Peso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        fecha = request.data.get('fecha')
        peso_valor = request.data.get('peso')
        imagen = request.FILES.get('imagen')
        
        if fecha:
            peso.fecha = fecha
        if peso_valor:
            peso.peso = peso_valor
        if imagen:
            peso.foto_pesaje = imagen

        peso.save()
        nuevo_peso_valido = PesoRegistrado.objects.filter(usuario=self.request.user).order_by('-fecha').first()
        peso_valor_nuevo = nuevo_peso_valido.peso
        actualizarTraEditarPeso(self.request.user, peso_valor_nuevo)
        # Opcional: devuelve el peso actualizado
        serializer = PesoRegistradoSerializer(peso, context={'request': request})
        return Response({'mensaje': 'Peso actualizado correctamente', 'peso': serializer.data}, status=status.HTTP_200_OK)

class Perfil(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        serializer = UsuarioEditarPerfilSerializer(usuario, context={'request': request})
        return Response({'Datos_Usuario': serializer.data})
    
    def delete(self, request):
        user = request.user

        # Creamos la respuesta primero
        response = Response({"detail": "Cuenta eliminada correctamente"}, status=204)

        # Borramos las cookies
        response.delete_cookie('token')
        response.delete_cookie('refresh_token')

        # Eliminamos el usuario
        user.delete()

        return response
    
    def put(self, request):
        user = request.user

        serializer = UsuarioEditarPerfilSerializer(user, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            usuario_actualizado = serializer.save()

            imagen = request.FILES.get('imagen_Perfil')
            if imagen:
                user.imagen_Perfil = imagen
                user.save()
                # Re-serializamos para devolver la URL actualizada
                serializer = UsuarioEditarPerfilSerializer(user, context={'request': request})

            actualizarTrasActualizar(usuario_actualizado)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class admin_panel_usuarios(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        usuarios = Usuario.objects.all()
        alimentos = Alimento.objects.all()

        usuarios_serializados = UsuarioSerializer(usuarios, many=True).data
        alimentos_serializados = AlimentoSerializer(alimentos, many=True).data

        return Response({
            "usuarios": usuarios_serializados,
            "alimentos": alimentos_serializados
        }, status=status.HTTP_200_OK)
    
class admin_panel_alimentos(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
       
        alimentos = Alimento.objects.all()
        alimentos_serializados = AlimentoSerializer(alimentos, many=True).data

        return Response(alimentos_serializados, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            alimento=Alimento.objects.get(pk=pk)
            alimento.delete()
            return Response({'mensaje':'Alimento eliminado'}, status=status.HTTP_200_OK)
        except Alimento.DoesNotExist:
            return Response({'error':'Alimento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            alimento = Alimento.objects.get(pk=pk)
        except Alimento.DoesNotExist:
            return Response({'error': 'Alimento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AlimentoSerializer(alimento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):        
        data = request.data.copy()

            # Obtener el último código existente
        ultimo_alimento = Alimento.objects.order_by('-codigo').first()
            
        if ultimo_alimento and ultimo_alimento.codigo.isdigit():
            nuevo_codigo = str(int(ultimo_alimento.codigo) + 1).zfill(len(ultimo_alimento.codigo))
        else:
            # Si no hay registros o el código no es numérico, empieza desde 0001
            nuevo_codigo = '0001'

        data['codigo'] = nuevo_codigo

        serializer = AlimentoSerializer(data=data)
        if serializer.is_valid():
            alimento = serializer.save()
            return Response(AlimentoSerializer(alimento).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Recetas(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        usuario = request.user
        listacomida = Comida.objects.filter(usuario=usuario)
        comidas_serializadas = ComidaSerializer(listacomida, many=True).data
        return Response({'Comidas': comidas_serializadas})
    
    def delete(self, request, pk):
        usuario = request.user
        comida = Comida.objects.get(id=pk, usuario=usuario)
        comida.delete()

        return Response({'detalle': 'Receta eliminada correctamente'}, status=status.HTTP_204_NO_CONTENT)

class IngredientesDeReceta(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            receta = Comida.objects.get(id=pk, usuario=request.user)
        except Comida.DoesNotExist:
            return Response({'error': 'Receta no encontrada.'}, status=404)

        ingredientes = AlimentoComida.objects.filter(comida=receta)
        serializer = AlimentoComidaSerializer(ingredientes, many=True)
        return Response({'ingredientes': serializer.data})

class ComidaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        comida = Comida.objects.get(id=pk, usuario=request.user)
        serializer = ComidaEditarSerializer(comida)
        return Response(serializer.data)

    def post(self, request):
        serializer = ComidaCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comida = serializer.save()
            return Response({'mensaje': 'Comida creada correctamente', 'comida_id': comida.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        comida = Comida.objects.get(id=pk, usuario=request.user)
        serializer = ComidaCreateSerializer(instance=comida, data=request.data, context={'request': request})
        if serializer.is_valid():
            # Borrar los ingredientes anteriores
            comida.alimentos.all().delete()

            # Actualizar campos básicos
            validated_data = serializer.validated_data
            comida.nombre = validated_data['nombre']
            comida.numeroPorciones = validated_data['numeroPorciones']

            total_cal = total_prot = total_grasas = total_carb = 0

            for item in validated_data['ingredientes']:
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

            return Response({'mensaje': 'Comida actualizada correctamente'}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)