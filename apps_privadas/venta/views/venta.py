from apps_privadas.inventario.views.base import BaseViewSet
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from apps_privadas.venta.models import Venta, DetalleVenta
from apps_privadas.venta.serializers import (
    VentaSerializer,
    CrearVentaSerializer,
    ActualizarVentaSerializer
)


class VentaViewSet(BaseViewSet):
    queryset = Venta.objects.select_related('usuario').prefetch_related('detalles').all()
    model = Venta
    serializer_class = VentaSerializer
    crear_serializer_class = CrearVentaSerializer
    actualizar_serializer_class = ActualizarVentaSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        usuario_id = data.pop('usuario_id')
        detalles_data = data.pop('detalles', [])

        venta = self.model.objects.create(
            usuario_id=usuario_id,
            tipo=data.get('tipo'),
            estado=data.get('estado', 'pendiente'),
            precio_total=data.get('precio_total', 0)
        )

        for detalle in detalles_data:
            precio_subtotal = float(detalle['cantidad']) * float(detalle['precio_unitario'])
            DetalleVenta.objects.create(
                venta=venta,
                variante_producto_id=detalle['variante_producto_id'],
                cantidad=detalle['cantidad'],
                precio_unitario=detalle['precio_unitario'],
                precio_subtotal=precio_subtotal
            )

        return Response(
            self.serializer_class(venta).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        usuario_id = data.pop('usuario_id', None)

        if usuario_id:
            data['usuario_id'] = usuario_id

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()

        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)