from apps_privadas.inventario.serializers.categoria import (
    CategoriaSerializer,
    CrearCategoriaSerializer,
    ActualizarCategoriaSerializer
)
from apps_privadas.inventario.serializers.marca import (
    MarcaSerializer,
    CrearMarcaSerializer,
    ActualizarMarcaSerializer
)
from apps_privadas.inventario.serializers.producto import (
    ProductoSerializer,
    CrearProductoSerializer,
    ActualizarProductoSerializer
)
from apps_privadas.inventario.serializers.variante_producto import (
    VarianteProductoSerializer,
    CrearVarianteProductoSerializer,
    ActualizarVarianteProductoSerializer
)
from apps_privadas.inventario.serializers.multimedia import (
    MultimedioSerializer,
    CrearMultimedioSerializer,
    ActualizarMultimedioSerializer,
    MultimedioConArchivoSerializer
)
from apps_privadas.inventario.serializers.producto_favorito import (
    ProductoFavoritoSerializer,
    CrearProductoFavoritoSerializer,
)

__all__ = [
    'CategoriaSerializer',
    'CrearCategoriaSerializer',
    'ActualizarCategoriaSerializer',
    'MarcaSerializer',
    'CrearMarcaSerializer',
    'ActualizarMarcaSerializer',
    'ProductoSerializer',
    'CrearProductoSerializer',
    'ActualizarProductoSerializer',
    'VarianteProductoSerializer',
    'CrearVarianteProductoSerializer',
    'ActualizarVarianteProductoSerializer',
    'MultimedioSerializer',
    'CrearMultimedioSerializer',
    'ActualizarMultimedioSerializer',
    'MultimedioConArchivoSerializer',
    'ProductoFavoritoSerializer',
    'CrearProductoFavoritoSerializer',
]
