from rest_framework import serializers
from apps_privadas.inventario.models import Multimedio


class MultimedioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Multimedio
        fields = ['id', 'nombre', 'archivo_url', 'tipo', 'es_principal', 'orden', 'producto', 'producto_nombre']
        read_only_fields = ['id']


class MultimedioConArchivoSerializer(serializers.Serializer):
    archivo = serializers.FileField()
    tipo = serializers.ChoiceField(choices=Multimedio.TIPO_CHOICES, default='imagen')
    es_principal = serializers.BooleanField(default=False)
    orden = serializers.IntegerField(default=0)
    producto_id = serializers.IntegerField()

    def validate_producto_id(self, value):
        from apps_privadas.inventario.models import Producto
        if not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value

    def validate(self, data):
        if data.get('tipo') == 'realidad_aumentada':
            from apps_privadas.inventario.models import Multimedio
            producto_id = data.get('producto_id')
            if Multimedio.objects.filter(producto_id=producto_id, tipo='realidad_aumentada').exists():
                raise serializers.ValidationError({
                    'tipo': 'Este producto ya tiene un archivo de realidad aumentada'
                })
        return data


class CrearMultimedioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255)
    archivo_url = serializers.URLField(max_length=500)
    tipo = serializers.ChoiceField(choices=Multimedio.TIPO_CHOICES)
    es_principal = serializers.BooleanField(default=False)
    orden = serializers.IntegerField(default=0)
    producto_id = serializers.IntegerField()

    def validate_producto_id(self, value):
        from apps_privadas.inventario.models import Producto
        if not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value

    def validate(self, data):
        if data.get('tipo') == 'realidad_aumentada':
            from apps_privadas.inventario.models import Multimedio
            producto_id = data.get('producto_id')
            if Multimedio.objects.filter(producto_id=producto_id, tipo='realidad_aumentada').exists():
                raise serializers.ValidationError({
                    'tipo': 'Este producto ya tiene un archivo de realidad aumentada'
                })
        return data


class ActualizarMultimedioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255, required=False)
    archivo_url = serializers.URLField(max_length=500, required=False)
    tipo = serializers.ChoiceField(choices=Multimedio.TIPO_CHOICES, required=False)
    es_principal = serializers.BooleanField(required=False)
    orden = serializers.IntegerField(required=False)
    producto_id = serializers.IntegerField(required=False)

    def validate_producto_id(self, value):
        if value:
            from apps_privadas.inventario.models import Producto
            if not Producto.objects.filter(id=value).exists():
                raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value

    def validate(self, data):
        instance = getattr(self, 'instance', None)
        tipo = data.get('tipo') or (instance.tipo if instance else None)
        producto_id = data.get('producto_id') or (instance.producto_id if instance else None)

        if tipo == 'realidad_aumentada' and producto_id:
            from apps_privadas.inventario.models import Multimedio
            query = Multimedio.objects.filter(producto_id=producto_id, tipo='realidad_aumentada')
            if instance:
                query = query.exclude(id=instance.id)
            if query.exists():
                raise serializers.ValidationError({
                    'tipo': 'Este producto ya tiene un archivo de realidad aumentada'
                })
        return data
