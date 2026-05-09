from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.compras.views import ProveedorViewSet, CompraViewSet

router = DefaultRouter()
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'compras', CompraViewSet, basename='compra')

app_name = 'compras'

urlpatterns = [
    path('', include(router.urls)),
]