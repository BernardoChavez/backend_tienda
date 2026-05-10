from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_publicas.empresas.views import EmpresaViewSet, PlanViewSet, SuscripcionViewSet, SuscripcionCambioViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'planes', PlanViewSet, basename='plan')
router.register(r'suscripciones', SuscripcionViewSet, basename='suscripcion')
router.register(r'suscripcion-cambios', SuscripcionCambioViewSet, basename='suscripcion-cambio')

app_name = 'empresas'

urlpatterns = [
    path('', include(router.urls)),
]
