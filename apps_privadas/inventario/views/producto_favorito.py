from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps_privadas.inventario.views.base import BaseViewSet
from apps_privadas.inventario.models import ProductoFavorito
from apps_privadas.inventario.serializers import (
    ProductoFavoritoSerializer,
    CrearProductoFavoritoSerializer,
)


class ProductoFavoritoViewSet(BaseViewSet):
    queryset = ProductoFavorito.objects.select_related('producto__categoria', 'producto__marca').all()
    model = ProductoFavorito
    serializer_class = ProductoFavoritoSerializer
    crear_serializer_class = CrearProductoFavoritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = self.queryset.filter(usuario=self.request.user)

        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(producto__categoria_id=categoria)

        marca = self.request.query_params.get('marca')
        if marca:
            qs = qs.filter(producto__marca_id=marca)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.crear_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        favorito, created = ProductoFavorito.objects.get_or_create(
            usuario=request.user,
            producto_id=serializer.validated_data['producto_id']
        )

        if not created:
            return Response(
                {'error': 'El producto ya está en favoritos'},
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            ProductoFavoritoSerializer(favorito).data,
            status=status.HTTP_201_CREATED
        )
