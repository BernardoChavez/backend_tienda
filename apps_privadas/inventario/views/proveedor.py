from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from apps_privadas.inventario.models import Proveedor
from apps_privadas.inventario.serializers import (
    ProveedorSerializer,
    CrearProveedorSerializer,
    ActualizarProveedorSerializer
)

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'telefono']

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearProveedorSerializer
        elif self.action in ['update', 'partial_update']:
            return ActualizarProveedorSerializer
        return ProveedorSerializer
