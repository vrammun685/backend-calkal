from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('token')
        if token is None:
            return None

        try:
            validated_token = self.get_validated_token(token)  # Intentamos validar el token
        except Exception as e:
            return None
        
        user = self.get_user(validated_token)  # Si el token es válido, obtenemos el usuario
        return user, validated_token  # Devolvemos el usuario y el token validado