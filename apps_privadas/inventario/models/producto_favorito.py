from django.db import models
from apps_privadas.inventario.models import Producto
from apps_privadas.seguridad.models.usuario import Usuario


class ProductoFavorito(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='usuarios_favoritos'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Producto Favorito'
        verbose_name_plural = 'Productos Favoritos'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'producto'],
                name='unique_usuario_producto_favorito'
            )
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"
