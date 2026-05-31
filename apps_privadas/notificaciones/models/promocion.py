from django.conf import settings
from django.db import models

from apps_privadas.inventario.models import Producto


class Promocion(models.Model):
    TIPO_PORCENTAJE = 'porcentaje'
    TIPO_MONTO_FIJO = 'monto_fijo'
    TIPO_DESCUENTO_CHOICES = [
        (TIPO_PORCENTAJE, 'Porcentaje'),
        (TIPO_MONTO_FIJO, 'Monto fijo'),
    ]

    ESTADO_BORRADOR = 'borrador'
    ESTADO_PUBLICADA = 'publicada'
    ESTADO_FINALIZADA = 'finalizada'
    ESTADO_CANCELADA = 'cancelada'
    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, 'Borrador'),
        (ESTADO_PUBLICADA, 'Publicada'),
        (ESTADO_FINALIZADA, 'Finalizada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='promociones'
    )
    tipo_descuento = models.CharField(max_length=20, choices=TIPO_DESCUENTO_CHOICES)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promociones_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Promocion'
        verbose_name_plural = 'Promociones'

    def __str__(self):
        return self.titulo

