from apps_privadas.inventario.views.base import BaseViewSet
from apps_privadas.inventario.models import Marca
from apps_privadas.inventario.serializers import (
    MarcaSerializer,
    CrearMarcaSerializer,
    ActualizarMarcaSerializer
)


class MarcaViewSet(BaseViewSet):
    queryset = Marca.objects.all()
    model = Marca
    serializer_class = MarcaSerializer
    crear_serializer_class = CrearMarcaSerializer
    actualizar_serializer_class = ActualizarMarcaSerializer
