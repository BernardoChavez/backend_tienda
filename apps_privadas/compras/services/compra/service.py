from decimal import Decimal
from django.db import transaction
from apps_privadas.compras.models import Compra, DetalleCompra
from apps_privadas.inventario.models import VarianteProducto


class CompraService:
    @staticmethod
    @transaction.atomic
    def crear_compra(proveedor_id):
        return Compra.objects.create(proveedor_id=proveedor_id, total=Decimal('0'))

    @staticmethod
    @transaction.atomic
    def aplicar_detalles(compra, detalles):
        total = Decimal('0')

        for detalle in detalles:
            cantidad = int(detalle['cantidad'])
            costo_unitario = Decimal(detalle['costo_unitario'])

            variante = VarianteProducto.objects.select_for_update().get(
                id=detalle['variante_producto_id']
            )

            costo_subtotal = costo_unitario * Decimal(cantidad)
            DetalleCompra.objects.create(
                compra=compra,
                variante_producto=variante,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                costo_subtotal=costo_subtotal,
            )

            stock_actual = int(variante.cantidad)
            nuevo_stock = stock_actual + cantidad

            costo_actual = Decimal(variante.costo_ponderado or 0)
            if nuevo_stock > 0:
                costo_ponderado = (
                    (costo_actual * Decimal(stock_actual)) + (costo_unitario * Decimal(cantidad))
                ) / Decimal(nuevo_stock)
            else:
                costo_ponderado = costo_unitario

            variante.cantidad = nuevo_stock
            variante.costo_ponderado = costo_ponderado
            variante.save(update_fields=['cantidad', 'costo_ponderado'])

            total += costo_subtotal

        if total != compra.total:
            compra.total = total
            compra.save(update_fields=['total'])

        return compra

