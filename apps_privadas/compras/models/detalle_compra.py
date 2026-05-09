from django.db import models
from apps_privadas.compras.models.compra import Compra
from apps_privadas.inventario.models import VarianteProducto


class DetalleCompra(models.Model):
    cantidad = models.PositiveIntegerField()
    costo_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    variante_producto = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        related_name='detalles_compra'
    )
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'

    def __str__(self):
        return f"Detalle {self.id} - Compra {self.compra.id}"