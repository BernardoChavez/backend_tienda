from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.decorators import action

from apps_privadas.compras.models import Compra
from apps_privadas.compras.serializers import (
    CompraSerializer,
    CrearCompraSerializer,
    ActualizarCompraSerializer,
    DetalleCompraSerializer,
)
from apps_privadas.compras.services.compra.service import CompraService


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

        compra = CompraService.crear_compra(proveedor_id)
        CompraService.aplicar_detalles(compra, detalles_data)

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

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        compra = self.get_object()
        detalles = compra.detalles.all()
        serializer = DetalleCompraSerializer(detalles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
