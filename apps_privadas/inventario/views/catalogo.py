from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps_privadas.inventario.models import Producto
from apps_privadas.inventario.serializers import ProductoSerializer
from apps_privadas.seguridad.permissions import CanViewCatalogo


class CatalogoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Producto.objects.select_related('categoria', 'marca').all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, CanViewCatalogo]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion']

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset

