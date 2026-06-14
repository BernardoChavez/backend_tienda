from rest_framework import serializers
from apps_privadas.inventario.models import ProductoFavorito, Producto, VarianteProducto, Multimedio
from django.db.models import Min


class ProductoFavoritoSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source='producto.id', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_precio = serializers.SerializerMethodField()
    producto_imagen = serializers.SerializerMethodField()

    class Meta:
        model = ProductoFavorito
        fields = ['id', 'usuario', 'producto_id', 'producto_nombre',
                  'producto_precio', 'producto_imagen', 'creado_en']
        read_only_fields = ['id', 'usuario', 'creado_en']

    def get_producto_precio(self, obj):
        min_precio = VarianteProducto.objects.filter(producto=obj.producto).aggregate(Min('precio'))['precio__min']
        return float(min_precio) if min_precio else 0

    def get_producto_imagen(self, obj):
        img = Multimedio.objects.filter(producto=obj.producto, tipo='imagen', es_principal=True).first()
        if not img:
            img = Multimedio.objects.filter(producto=obj.producto, tipo='imagen').first()
        return img.archivo_url if img else None


class CrearProductoFavoritoSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()

    def validate_producto_id(self, value):
        if not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError("El producto no existe")
        return value
