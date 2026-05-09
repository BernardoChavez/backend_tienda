from rest_framework import serializers
from apps_privadas.inventario.models import Producto, Categoria, Multimedio, Marca


class MultimedioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Multimedio
        fields = ['id', 'archivo_url', 'tipo', 'es_principal', 'orden']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    imagenes = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'activo', 'categoria', 'categoria_nombre', 'marca', 'marca_nombre', 'imagenes']
        read_only_fields = ['id']

    def get_imagenes(self, obj):
        multimedia = Multimedio.objects.filter(producto=obj, tipo='imagen')
        return MultimedioSimpleSerializer(multimedia, many=True).data


class CrearProductoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200)
    descripcion = serializers.CharField(required=False, default='')
    activo = serializers.BooleanField(required=False, default=True)
    categoria_id = serializers.IntegerField()
    marca_id = serializers.IntegerField()

    def validate_categoria_id(self, value):
        if not Categoria.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La categoría con ID {value} no existe')
        return value

    def validate_marca_id(self, value):
        if not Marca.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La marca con ID {value} no existe')
        return value


class ActualizarProductoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200, required=False)
    descripcion = serializers.CharField(required=False)
    activo = serializers.BooleanField(required=False)
    categoria_id = serializers.IntegerField(required=False)
    marca_id = serializers.IntegerField(required=False)

    def validate_categoria_id(self, value):
        if value and not Categoria.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La categoría con ID {value} no existe')
        return value

    def validate_marca_id(self, value):
        if value and not Marca.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La marca con ID {value} no existe')
        return value
