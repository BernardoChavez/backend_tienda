from rest_framework import serializers
from apps_privadas.carrito.models import Carrito, DetalleCarrito
from apps_privadas.inventario.serializers.variante_producto import VarianteProductoSerializer

class DetalleCarritoSerializer(serializers.ModelSerializer):
    variante_producto_info = VarianteProductoSerializer(source='variante_producto', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = DetalleCarrito
        fields = ['id', 'variante_producto', 'variante_producto_info', 'cantidad', 'subtotal']

class CarritoSerializer(serializers.ModelSerializer):
    detalles = DetalleCarritoSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'usuario_username', 'detalles', 'total', 'fecha_actualizacion']
