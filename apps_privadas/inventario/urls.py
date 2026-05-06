from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.inventario.views import CategoriaViewSet, ProductoViewSet, MultimedioViewSet, ProveedorViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'multimedios', MultimedioViewSet, basename='multimedio')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')

app_name = 'inventario'

urlpatterns = [
    path('', include(router.urls)),
]
