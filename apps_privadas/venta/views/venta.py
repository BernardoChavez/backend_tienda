from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from apps_privadas.inventario.views.base import BaseViewSet
from apps_privadas.inventario.models import VarianteProducto
from apps_privadas.venta.models import Venta, DetalleVenta
from apps_privadas.venta.serializers import (
    VentaSerializer,
    CrearVentaSerializer,
    ActualizarVentaSerializer,
)
from apps_privadas.ia.services.alertas_service import verificar_stock_post_venta


class VentaViewSet(BaseViewSet):
    queryset = Venta.objects.select_related('usuario').prefetch_related('detalles__variante_producto__producto').all()
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
            variante = VarianteProducto.objects.select_for_update().get(
                id=detalle['variante_producto_id']
            )
            cantidad = detalle['cantidad']

            if variante.cantidad < cantidad:
                raise ValidationError(
                    f'Stock insuficiente para {variante.sku}. '
                    f'Disponible: {variante.cantidad}, solicitado: {cantidad}'
                )

            variante.cantidad -= cantidad
            variante.save()
            verificar_stock_post_venta(variante)

            precio_subtotal = float(cantidad) * float(detalle['precio_unitario'])
            DetalleVenta.objects.create(
                venta=venta,
                variante_producto_id=detalle['variante_producto_id'],
                cantidad=cantidad,
                precio_unitario=detalle['precio_unitario'],
                precio_subtotal=precio_subtotal
            )

        total = sum(
            DetalleVenta.objects.filter(venta=venta)
            .values_list('precio_subtotal', flat=True)
        )
        venta.precio_total = total
        venta.save()

        return Response(
            self.serializer_class(venta).data,
            status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()

        detalles_data = data.pop('detalles', None)

        usuario_id = data.pop('usuario_id', None)
        if usuario_id:
            data['usuario_id'] = usuario_id

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()

        if detalles_data is not None:
            existing_ids = set(
                DetalleVenta.objects.filter(venta=instance)
                .values_list('id', flat=True)
            )
            incoming_ids = set()

            for detalle_data in detalles_data:
                detalle_id = detalle_data.get('id')
                variante_id = detalle_data['variante_producto_id']
                nueva_cantidad = detalle_data['cantidad']
                precio_unitario = detalle_data['precio_unitario']

                variante = VarianteProducto.objects.select_for_update().get(id=variante_id)

                if detalle_id and detalle_id in existing_ids:
                    detalle = DetalleVenta.objects.get(id=detalle_id, venta=instance)
                    old_cantidad = detalle.cantidad
                    diferencia = nueva_cantidad - old_cantidad

                    if diferencia > 0 and variante.cantidad < diferencia:
                        raise ValidationError(
                            f'Stock insuficiente para {variante.sku}. '
                            f'Disponible: {variante.cantidad}, necesita {diferencia} adicionales'
                        )

                    variante.cantidad -= diferencia
                    variante.save()

                    detalle.cantidad = nueva_cantidad
                    detalle.precio_unitario = precio_unitario
                    detalle.precio_subtotal = float(nueva_cantidad) * float(precio_unitario)
                    detalle.save()
                    incoming_ids.add(detalle_id)
                else:
                    if variante.cantidad < nueva_cantidad:
                        raise ValidationError(
                            f'Stock insuficiente para {variante.sku}. '
                            f'Disponible: {variante.cantidad}, solicitado: {nueva_cantidad}'
                        )

                    variante.cantidad -= nueva_cantidad
                    variante.save()

                    detalle = DetalleVenta.objects.create(
                        venta=instance,
                        variante_producto_id=variante_id,
                        cantidad=nueva_cantidad,
                        precio_unitario=precio_unitario,
                        precio_subtotal=float(nueva_cantidad) * float(precio_unitario)
                    )
                    if detalle_id:
                        incoming_ids.add(detalle.id)

            to_delete = existing_ids - incoming_ids
            for det_id in to_delete:
                detalle = DetalleVenta.objects.get(id=det_id, venta=instance)
                variante = VarianteProducto.objects.select_for_update().get(
                    id=detalle.variante_producto_id
                )
                variante.cantidad += detalle.cantidad
                variante.save()
                detalle.delete()

            total = sum(
                DetalleVenta.objects.filter(venta=instance)
                .values_list('precio_subtotal', flat=True)
            )
            instance.precio_total = total
            instance.save()

        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
