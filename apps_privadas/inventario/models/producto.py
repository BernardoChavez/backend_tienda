from django.db import models
from apps_privadas.inventario.models.categoria import Categoria
from apps_privadas.inventario.models.proveedor import Proveedor


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
