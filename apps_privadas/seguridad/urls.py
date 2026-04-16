from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.seguridad.views import (
    UsuarioViewSet,
    RolViewSet,
    login,
    solicitar_recuperacion,
    verificar_codigo,
    cambiar_password,
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet, basename='rol')

app_name = 'seguridad'

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login, name='login'),
    path('recuperar-password/solicitar/', solicitar_recuperacion, name='recuperar-solicitar'),
    path('recuperar-password/verificar/', verificar_codigo, name='recuperar-verificar'),
    path('recuperar-password/cambiar/', cambiar_password, name='recuperar-cambiar'),
]

