from django.db import models
from apps_privadas.inventario.models import Producto


class Multimedio(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('realidad_aumentada', 'Realidad Aumentada'),
    ]

    archivo_url = models.URLField(max_length=500, blank=True, default='')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='multimedios'
    )

    class Meta:
        ordering = ['orden']
        verbose_name = 'Multimedio'
        verbose_name_plural = 'Multimedios'

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre}"
