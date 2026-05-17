from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.inventario.views import (
    CategoriaViewSet,
    MarcaViewSet,
    ProductoViewSet,
    VarianteProductoViewSet,
    MultimedioViewSet,
    CatalogoViewSet,
    ProductoDetalleViewSet,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'variantes', VarianteProductoViewSet, basename='variante-producto')
router.register(r'multimedios', MultimedioViewSet, basename='multimedio')
router.register(r'catalogo', CatalogoViewSet, basename='catalogo')
router.register(r'productos-detalle', ProductoDetalleViewSet, basename='producto-detalle')

app_name = 'inventario'

urlpatterns = [
    path('', include(router.urls)),
]
