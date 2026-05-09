from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.venta.views import VentaViewSet

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='venta')

app_name = 'venta'

urlpatterns = [
    path('', include(router.urls)),
]