from django.db import models
from apps_privadas.inventario.models import Producto


class VarianteProducto(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=0)
    costo_ponderado = models.DecimalField(max_digits=10, decimal_places=2)
    limite_cantidad = models.PositiveIntegerField(default=0)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='variantes'
    )

    class Meta:
        ordering = ['sku']
        verbose_name = 'Variante de Producto'
        verbose_name_plural = 'Variantes de Producto'

    def __str__(self):
        return f"{self.sku} - {self.producto.nombre}"
