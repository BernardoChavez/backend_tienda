from apps_privadas.inventario.views.base import BaseViewSet
from apps_privadas.inventario.models import VarianteProducto
from apps_privadas.inventario.serializers import (
    VarianteProductoSerializer,
    CrearVarianteProductoSerializer,
    ActualizarVarianteProductoSerializer
)


class VarianteProductoViewSet(BaseViewSet):
    queryset = VarianteProducto.objects.select_related('producto').all()
    model = VarianteProducto
    serializer_class = VarianteProductoSerializer
    crear_serializer_class = CrearVarianteProductoSerializer
    actualizar_serializer_class = ActualizarVarianteProductoSerializer

    def get_queryset(self):
        qs = VarianteProducto.objects.select_related('producto').all()
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            qs = qs.filter(producto_id=producto_id)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        producto_id = serializer.validated_data.pop('producto_id')

        instance = self.model.objects.create(
            producto_id=producto_id,
            **serializer.validated_data
        )

        from rest_framework import status
        from rest_framework.response import Response
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        producto_id = data.pop('producto_id', None)

        if producto_id:
            data['producto_id'] = producto_id

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()

        from rest_framework import status
        from rest_framework.response import Response
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
