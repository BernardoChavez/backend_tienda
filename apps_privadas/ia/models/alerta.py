from django.db import models
from apps_privadas.inventario.models import VarianteProducto


class AlertaReabastecimiento(models.Model):
    TIPO_CHOICES = [
        ('stock_bajo', 'Stock Bajo'),
        ('demanda_alta', 'Demanda Proyectada Alta'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        related_name='alertas_reabastecimiento'
    )
    stock_actual = models.PositiveIntegerField()
    limite_minimo = models.PositiveIntegerField()
    demanda_proyectada = models.PositiveIntegerField(null=True, blank=True)
    dias_proyectados = models.PositiveIntegerField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Alerta de Reabastecimiento'
        verbose_name_plural = 'Alertas de Reabastecimiento'

    def __str__(self):
        return f"[{self.tipo}] {self.variante.sku} - Stock: {self.stock_actual}/{self.limite_minimo}"
