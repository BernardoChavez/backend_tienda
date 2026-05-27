from django.db import models
from apps_privadas.inventario.models.categoria import Categoria
from apps_privadas.inventario.models.marca import Marca


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    activo = models.BooleanField(default=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    embedding = models.JSONField(null=True, blank=True)
    embedding_sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('processing', 'Procesando'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
        ],
        default='pending'
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        permissions = [
            ('view_catalogo', 'Puede ver el catalogo'),
            ('view_producto_detalle', 'Puede ver detalle de producto'),
        ]

    def __str__(self):
        return self.nombre
