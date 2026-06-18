from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.ia.views.alertas import AlertaReabastecimientoViewSet
from apps_privadas.ia.views.dashboard import DashboardVentasView
from apps_privadas.ia.views.prediccion_detalle import PrediccionDetalleView
from apps_privadas.ia.views.reentrenar import ReentrenarView

router = DefaultRouter()
router.register('ia/alertas', AlertaReabastecimientoViewSet, basename='alertas-reabastecimiento')

urlpatterns = [
    path('', include(router.urls)),
    path('ia/dashboard/', DashboardVentasView.as_view(), name='ia-dashboard'),
    path('ia/prediccion-detalle/', PrediccionDetalleView.as_view(), name='ia-prediccion-detalle'),
    path('ia/reentrenar/', ReentrenarView.as_view(), name='ia-reentrenar'),
]
