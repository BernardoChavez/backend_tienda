from rest_framework import serializers
from apps_privadas.inventario.models import Marca


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre']


class CrearMarcaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)

    def validate_nombre(self, value):
        if Marca.objects.filter(nombre=value).exists():
            raise serializers.ValidationError(f'La marca "{value}" ya existe')
        return value


class ActualizarMarcaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100, required=False)

    def validate_nombre(self, value):
        if value:
            existe = Marca.objects.filter(nombre=value).exclude(
                id=self.instance.id if self.instance else None
            ).exists()
            if existe:
                raise serializers.ValidationError(f'La marca "{value}" ya existe')
        return value
