from rest_framework import serializers
from apps_privadas.inventario.models import Producto, Categoria, Multimedio, Proveedor


class MultimedioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Multimedio
        fields = ['id', 'nombre', 'archivo_url', 'es_principal', 'orden']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    imagenes = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'codigo', 'nombre', 'precio', 'categoria', 'categoria_nombre', 'proveedor', 'imagenes']
        read_only_fields = ['id']

    def get_imagenes(self, obj):
        multimedia = Multimedio.objects.filter(producto=obj, tipo='imagen')
        return MultimedioSimpleSerializer(multimedia, many=True).data


class CrearProductoSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=200)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    categoria_id = serializers.IntegerField()
    proveedor_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_codigo(self, value):
        if Producto.objects.filter(codigo=value).exists():
            raise serializers.ValidationError(f'El código "{value}" ya existe')
        return value

    def validate_categoria_id(self, value):
        if not Categoria.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La categoría con ID {value} no existe')
        return value

    def validate_proveedor_id(self, value):
        if value and not Proveedor.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El proveedor con ID {value} no existe')
        return value


class ActualizarProductoSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=50, required=False)
    nombre = serializers.CharField(max_length=200, required=False)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    categoria_id = serializers.IntegerField(required=False)
    proveedor_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_codigo(self, value):
        if value:
            existe = Producto.objects.filter(codigo=value).exclude(
                id=self.instance.id if self.instance else None
            ).exists()
            if existe:
                raise serializers.ValidationError(f'El código "{value}" ya existe')
        return value

    def validate_categoria_id(self, value):
        if value and not Categoria.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La categoría con ID {value} no existe')
        return value

    def validate_proveedor_id(self, value):
        if value and not Proveedor.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El proveedor con ID {value} no existe')
        return value
