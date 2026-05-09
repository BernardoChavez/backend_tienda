from django.db import models
from apps_privadas.venta.models.venta import Venta
from apps_privadas.inventario.models import VarianteProducto


class DetalleVenta(models.Model):
    cantidad = models.PositiveIntegerField()
    precio_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    variante_producto = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        related_name='detalles_venta'
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

    def __str__(self):
        return f"Detalle {self.id} - Venta {self.venta.id}"