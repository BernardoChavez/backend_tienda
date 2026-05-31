from django.conf import settings
from django.db import models


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones_push'
    )
    endpoint = models.URLField(max_length=1000, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user_agent = models.TextField(blank=True, default='')
    activa = models.BooleanField(default=True)
    ultima_promocion = models.ForeignKey(
        'notificaciones.Promocion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones_enviadas'
    )
    ultimo_envio = models.DateTimeField(null=True, blank=True)
    ultimo_error = models.TextField(blank=True, default='')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_actualizacion']
        verbose_name = 'Notificacion push'
        verbose_name_plural = 'Notificaciones push'

    def __str__(self):
        return f"{self.usuario_id} - {self.endpoint[:50]}"

