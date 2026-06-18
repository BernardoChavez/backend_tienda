from django.db import models


class ModeloEntrenado(models.Model):
    TIPO_CHOICES = [
        ('random_forest', 'Random Forest'),
        ('prophet', 'Prophet'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    ruta_archivo = models.CharField(max_length=500)
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    total_registros = models.IntegerField()
    vigente = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_entrenamiento']
        verbose_name = 'Modelo Entrenado'
        verbose_name_plural = 'Modelos Entrenados'

    def __str__(self):
        return f"[{self.tipo}] {self.fecha_entrenamiento:%Y-%m-%d %H:%M} — {self.total_registros} registros"
