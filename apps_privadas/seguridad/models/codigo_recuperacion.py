from django.db import models
from django.utils import timezone

from apps_privadas.seguridad.models.usuario import Usuario


class CodigoRecuperacion(models.Model):
    """
    Almacena los codigos temporales para recuperacion de contrasena.
    Expira a los 15 minutos de su creacion.
    """

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='codigos_recuperacion'
    )
    codigo = models.CharField(max_length=8)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Codigo de Recuperacion'
        verbose_name_plural = 'Codigos de Recuperacion'

    def esta_vigente(self):
        return not self.usado and timezone.now() < self.expira_en

    def __str__(self):
        return f"{self.usuario.username} - {self.codigo}"
