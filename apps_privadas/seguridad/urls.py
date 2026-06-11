from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.seguridad.views.usuarios import UsuarioViewSet
from apps_privadas.seguridad.views.roles import RolViewSet
from apps_privadas.seguridad.views.auth import (
    login,
    solicitar_recuperacion,
    verificar_codigo,
    cambiar_password,
)
from apps_privadas.seguridad.views.bitacora import BitacoraAuditoriaViewSet
from apps_privadas.seguridad.views.backup_automatico import AutomaticBackupSimulatedView

# Router para ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'bitacora', BitacoraAuditoriaViewSet, basename='bitacora')

app_name = 'seguridad'

urlpatterns = [
    path('', include(router.urls)),
    path('backup/automatico/', AutomaticBackupSimulatedView.as_view(), name='backup-automatico'),
    path('login/', login, name='login'),
    path('recuperar-password/solicitar/', solicitar_recuperacion, name='recuperar-solicitar'),
    path('recuperar-password/verificar/', verificar_codigo, name='recuperar-verificar'),
    path('recuperar-password/cambiar/', cambiar_password, name='recuperar-cambiar'),
]
