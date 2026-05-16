from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    """Serializer para autenticar usuarios y retornar JWT"""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validar credenciales"""
        username = data.get('username')
        password = data.get('password')

        # Intentar autenticar
        usuario = authenticate(username=username, password=password)

        if usuario is None:
            raise serializers.ValidationError(
                "Usuario o contrasena incorrectos"
            )

        if not usuario.is_active:
            raise serializers.ValidationError(
                "Este usuario esta desactivado"
            )

        data['usuario'] = usuario
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado que incluye el id del usuario en el token"""

    def get_token(self, user):
        token = super().get_token(user)

        # Agregar campos personalizados al token
        token['usuario_id'] = user.id
        token['username'] = user.username
        token['nombre_completo'] = user.nombre_completo

        return token

