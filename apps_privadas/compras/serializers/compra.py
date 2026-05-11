from rest_framework import serializers
from apps_privadas.compras.models import Compra, DetalleCompra


class DetalleCompraInputSerializer(serializers.Serializer):
    variante_producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    costo_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_variante_producto_id(self, value):
        from apps_privadas.inventario.models import VarianteProducto
        if not VarianteProducto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La variante con ID {value} no existe')
        return value


class CompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model = Compra
        fields = ['id', 'fecha', 'total', 'proveedor', 'proveedor_nombre']
        read_only_fields = ['id', 'fecha']


class DetalleCompraSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(source='variante_producto.sku', read_only=True)
    producto_nombre = serializers.CharField(source='variante_producto.producto.nombre', read_only=True)

    class Meta:
        model = DetalleCompra
        fields = [
            'id',
            'compra',
            'variante_producto',
            'sku',
            'producto_nombre',
            'cantidad',
            'costo_unitario',
            'costo_subtotal',
        ]
        read_only_fields = ['id']


class CrearCompraSerializer(serializers.Serializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    proveedor_id = serializers.IntegerField()
    detalles = serializers.ListField(
        child=DetalleCompraInputSerializer(),
        required=False,
        allow_empty=True
    )

    def validate_proveedor_id(self, value):
        from apps_privadas.compras.models import Proveedor
        if not Proveedor.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El proveedor con ID {value} no existe')
        return value


class ActualizarCompraSerializer(serializers.Serializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    proveedor_id = serializers.IntegerField(required=False)

    def validate_proveedor_id(self, value):
        if value:
            from apps_privadas.compras.models import Proveedor
            if not Proveedor.objects.filter(id=value).exists():
                raise serializers.ValidationError(f'El proveedor con ID {value} no existe')
        return value