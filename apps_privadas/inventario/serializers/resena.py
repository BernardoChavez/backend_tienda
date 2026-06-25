from rest_framework import serializers
from apps_privadas.inventario.models.resena import Resena


class ResenaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Resena
        fields = [
            'id',
            'usuario',
            'usuario_username',
            'producto',
            'calificacion',
            'comentario',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'usuario', 'usuario_username', 'fecha_creacion', 'fecha_actualizacion']


class CrearResenaSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    calificacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_producto_id(self, value):
        from apps_privadas.inventario.models.producto import Producto
        if not Producto.objects.filter(id=value, activo=True).exists():
            raise serializers.ValidationError('El producto no existe o no está activo.')
        return value


class ActualizarResenaSerializer(serializers.Serializer):
    calificacion = serializers.IntegerField(min_value=1, max_value=5, required=False)
    comentario = serializers.CharField(required=False, allow_blank=True)