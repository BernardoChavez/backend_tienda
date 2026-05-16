from rest_framework import serializers


class SolicitarRecuperacionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)


class VerificarCodigoSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    codigo = serializers.CharField(max_length=8, min_length=6)


class CambiarPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    codigo = serializers.CharField(max_length=8, min_length=6)
    nueva_password = serializers.CharField(write_only=True, min_length=8)

