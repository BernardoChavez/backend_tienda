from rest_framework import serializers
from apps_privadas.inventario.models.proveedor import Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'direccion', 'telefono']

class CrearProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'direccion', 'telefono']

class ActualizarProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'direccion', 'telefono']