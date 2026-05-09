from rest_framework import serializers
from apps_privadas.venta.models import Venta
from apps_privadas.inventario.models import VarianteProducto


class DetalleVentaInputSerializer(serializers.Serializer):
    variante_producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_variante_producto_id(self, value):
        if not VarianteProducto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La variante con ID {value} no existe')
        return value


class VentaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'tipo', 'estado', 'fecha', 'precio_total', 'usuario', 'usuario_username']
        read_only_fields = ['id', 'fecha']


class CrearVentaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Venta.TIPO_CHOICES)
    estado = serializers.ChoiceField(choices=Venta.ESTADO_CHOICES, default='pendiente')
    precio_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    usuario_id = serializers.IntegerField()
    detalles = serializers.ListField(
        child=DetalleVentaInputSerializer(),
        required=False,
        allow_empty=True
    )

    def validate_usuario_id(self, value):
        from apps_privadas.seguridad.models import Usuario
        if not Usuario.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El usuario con ID {value} no existe')
        return value


class ActualizarVentaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Venta.TIPO_CHOICES, required=False)
    estado = serializers.ChoiceField(choices=Venta.ESTADO_CHOICES, required=False)
    precio_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    usuario_id = serializers.IntegerField(required=False)

    def validate_usuario_id(self, value):
        if value:
            from apps_privadas.seguridad.models import Usuario
            if not Usuario.objects.filter(id=value).exists():
                raise serializers.ValidationError(f'El usuario con ID {value} no existe')
        return value