from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps_privadas.notificaciones.views import NotificacionViewSet, PromocionViewSet


router = DefaultRouter()
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')
router.register(r'promociones', PromocionViewSet, basename='promocion')

app_name = 'notificaciones'

urlpatterns = [
    path('', include(router.urls)),
]

