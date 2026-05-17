from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps_privadas.inventario.models import Producto
from apps_privadas.inventario.serializers import ProductoSerializer
from apps_privadas.seguridad.permissions import CanViewProductoDetalle


class ProductoDetalleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Producto.objects.select_related('categoria', 'marca').all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, CanViewProductoDetalle]

    def list(self, request, *args, **kwargs):
        return Response({'error': 'Listado no permitido'}, status=status.HTTP_403_FORBIDDEN)

