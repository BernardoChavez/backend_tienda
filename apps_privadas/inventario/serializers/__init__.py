from apps_privadas.inventario.serializers.categoria import (
    CategoriaSerializer,
    CrearCategoriaSerializer,
    ActualizarCategoriaSerializer
)
from apps_privadas.inventario.serializers.producto import (
    ProductoSerializer,
    CrearProductoSerializer,
    ActualizarProductoSerializer
)
from apps_privadas.inventario.serializers.multimedia import (
    MultimedioSerializer,
    CrearMultimedioSerializer,
    ActualizarMultimedioSerializer,
    MultimedioConArchivoSerializer
)

__all__ = [
    'CategoriaSerializer',
    'CrearCategoriaSerializer',
    'ActualizarCategoriaSerializer',
    'ProductoSerializer',
    'CrearProductoSerializer',
    'ActualizarProductoSerializer',
    'MultimedioSerializer',
    'CrearMultimedioSerializer',
    'ActualizarMultimedioSerializer'
    'MultimedioConArchivoSerializer'
]
