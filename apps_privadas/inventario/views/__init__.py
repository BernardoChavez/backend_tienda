from apps_privadas.inventario.views.categoria import CategoriaViewSet
from apps_privadas.inventario.views.marca import MarcaViewSet
from apps_privadas.inventario.views.producto import ProductoViewSet
from apps_privadas.inventario.views.variante_producto import VarianteProductoViewSet
from apps_privadas.inventario.views.multimedia import MultimedioViewSet
from apps_privadas.inventario.views.catalogo import CatalogoViewSet
from apps_privadas.inventario.views.producto_detalle import ProductoDetalleViewSet

__all__ = [
    'CategoriaViewSet',
    'MarcaViewSet',
    'ProductoViewSet',
    'VarianteProductoViewSet',
    'MultimedioViewSet',
    'CatalogoViewSet',
    'ProductoDetalleViewSet',
]
