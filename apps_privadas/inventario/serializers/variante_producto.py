from rest_framework import serializers
from apps_privadas.inventario.models import VarianteProducto, Producto


class VarianteProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = VarianteProducto
        fields = ['id', 'sku', 'precio', 'cantidad', 'costo_ponderado', 'limite_cantidad', 'producto', 'producto_nombre']
        read_only_fields = ['id']


class CrearVarianteProductoSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=100)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    cantidad = serializers.IntegerField()
    costo_ponderado = serializers.DecimalField(max_digits=10, decimal_places=2)
    limite_cantidad = serializers.IntegerField()
    producto_id = serializers.IntegerField()

    def validate_sku(self, value):
        if VarianteProducto.objects.filter(sku=value).exists():
            raise serializers.ValidationError(f'El SKU "{value}" ya existe')
        return value

    def validate_producto_id(self, value):
        if not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value


class ActualizarVarianteProductoSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=100, required=False)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    cantidad = serializers.IntegerField(required=False)
    costo_ponderado = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    limite_cantidad = serializers.IntegerField(required=False)
    producto_id = serializers.IntegerField(required=False)

    def validate_sku(self, value):
        if value:
            existe = VarianteProducto.objects.filter(sku=value).exclude(
                id=self.instance.id if self.instance else None
            ).exists()
            if existe:
                raise serializers.ValidationError(f'El SKU "{value}" ya existe')
        return value

    def validate_producto_id(self, value):
        if value and not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value
