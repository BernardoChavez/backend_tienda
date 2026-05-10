from django.db import models
from apps_privadas.carrito.models.carrito import Carrito
from apps_privadas.inventario.models import VarianteProducto

class DetalleCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    variante_producto = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Detalle de Carrito'
        verbose_name_plural = 'Detalles de Carrito'
        unique_together = ('carrito', 'variante_producto')

    @property
    def subtotal(self):
        return self.variante_producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.variante_producto} en carrito de {self.carrito.usuario.username}"
