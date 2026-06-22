from django.db import models


class BitacoraAuditoria(models.Model):
    id_bitacora = models.BigAutoField(primary_key=True, db_column='id_bitacora')
    fecha = models.DateField()
    hora = models.TimeField()
    entidad = models.CharField(max_length=100)
    detalles = models.CharField(max_length=500)
    accion = models.CharField(max_length=100)
    usuarios_id = models.BigIntegerField(db_column='usuarios_id')
    usuario_username = models.CharField(max_length=150, blank=True, null=True)
    metodo = models.CharField(max_length=10, blank=True, null=True)
    ruta = models.CharField(max_length=255, blank=True, null=True)
    ip_cliente = models.GenericIPAddressField(blank=True, null=True)
    estado_http = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'bitacora'
        ordering = ['-fecha', '-hora', '-id_bitacora']
        verbose_name = 'Bitacora de auditoria'
        verbose_name_plural = 'Bitacoras de auditoria'

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.accion} - {self.entidad}"

