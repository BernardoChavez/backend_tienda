from django.utils import timezone
from rest_framework import serializers

from apps_privadas.inventario.models import Producto
from apps_privadas.notificaciones.models import Promocion


class PromocionSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source='producto.id', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)

    class Meta:
        model = Promocion
        fields = [
            'id',
            'titulo',
            'descripcion',
            'producto',
            'producto_id',
            'producto_nombre',
            'tipo_descuento',
            'valor_descuento',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'creado_por',
            'creado_por_username',
            'fecha_creacion',
            'fecha_actualizacion',
            'fecha_publicacion',
        ]
        read_only_fields = [
            'id',
            'estado',
            'creado_por',
            'creado_por_username',
            'fecha_creacion',
            'fecha_actualizacion',
            'fecha_publicacion',
        ]


class CrearPromocionSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=150)
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')
    producto_id = serializers.IntegerField()
    tipo_descuento = serializers.ChoiceField(choices=Promocion.TIPO_DESCUENTO_CHOICES)
    valor_descuento = serializers.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField()

    def validate_producto_id(self, value):
        if not Producto.objects.filter(id=value, activo=True).exists():
            raise serializers.ValidationError('El producto no existe o no esta activo.')
        return value

    def validate(self, attrs):
        if attrs['fecha_fin'] <= attrs['fecha_inicio']:
            raise serializers.ValidationError('La fecha fin debe ser posterior a la fecha inicio.')
        if attrs['fecha_fin'] <= timezone.now():
            raise serializers.ValidationError('La fecha fin debe ser futura.')
        if attrs['valor_descuento'] <= 0:
            raise serializers.ValidationError('El descuento debe ser mayor a cero.')
        if attrs['tipo_descuento'] == Promocion.TIPO_PORCENTAJE and attrs['valor_descuento'] > 100:
            raise serializers.ValidationError('El porcentaje no puede ser mayor a 100.')
        return attrs


class ActualizarPromocionSerializer(CrearPromocionSerializer):
    titulo = serializers.CharField(max_length=150, required=False)
    producto_id = serializers.IntegerField(required=False)
    tipo_descuento = serializers.ChoiceField(choices=Promocion.TIPO_DESCUENTO_CHOICES, required=False)
    valor_descuento = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    fecha_inicio = serializers.DateTimeField(required=False)
    fecha_fin = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')
        valor_descuento = attrs.get('valor_descuento')
        tipo_descuento = attrs.get('tipo_descuento')

        if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError('La fecha fin debe ser posterior a la fecha inicio.')
        if fecha_fin and fecha_fin <= timezone.now():
            raise serializers.ValidationError('La fecha fin debe ser futura.')
        if valor_descuento is not None and valor_descuento <= 0:
            raise serializers.ValidationError('El descuento debe ser mayor a cero.')
        if tipo_descuento == Promocion.TIPO_PORCENTAJE and valor_descuento is not None and valor_descuento > 100:
            raise serializers.ValidationError('El porcentaje no puede ser mayor a 100.')
        return attrs

