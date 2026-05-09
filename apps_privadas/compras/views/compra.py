from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps_privadas.compras.models import Compra, DetalleCompra
from apps_privadas.compras.serializers import (
    CompraSerializer,
    CrearCompraSerializer,
    ActualizarCompraSerializer
)


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.select_related('proveedor').prefetch_related('detalles').all()
    permission_classes = [IsAuthenticated]
    model = Compra
    serializer_class = CompraSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearCompraSerializer
        elif self.action in ['update', 'partial_update']:
            return ActualizarCompraSerializer
        return CompraSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = CrearCompraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        proveedor_id = data.pop('proveedor_id')
        detalles_data = data.pop('detalles', [])

        compra = Compra.objects.create(
            proveedor_id=proveedor_id,
            total=data.get('total', 0)
        )

        for detalle in detalles_data:
            costo_subtotal = float(detalle['cantidad']) * float(detalle['costo_unitario'])
            DetalleCompra.objects.create(
                compra=compra,
                variante_producto_id=detalle['variante_producto_id'],
                cantidad=detalle['cantidad'],
                costo_unitario=detalle['costo_unitario'],
                costo_subtotal=costo_subtotal
            )

        return Response(
            CompraSerializer(compra).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ActualizarCompraSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        proveedor_id = data.pop('proveedor_id', None)

        if proveedor_id:
            data['proveedor_id'] = proveedor_id

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()

        return Response(
            CompraSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)