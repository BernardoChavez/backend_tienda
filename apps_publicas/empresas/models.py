from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_tenants.models import TenantMixin, DomainMixin


# Create your models here.
class Empresa(TenantMixin):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True, null=True)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    auto_create_schema = True

class Dominio(DomainMixin):
    pass

class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    activo = models.BooleanField(default=True)

    # 1. LÍMITES NUMÉRICOS (Requieren contadores)
    limite_usuarios = models.IntegerField(default=5)
    limite_productos = models.IntegerField(default=50)
    limite_clientes = models.IntegerField(default=100)
    limite_proveedores = models.IntegerField(default=10)

    # 2. FUNCIONALIDADES / FEATURES (Booleanos)
    feature_realidad_aumentada = models.BooleanField(default=False)
    feature_fotos_3d = models.BooleanField(default=False)
    feature_reportes_dinamicos = models.BooleanField(default=False)
    feature_backup_automatico = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'

    def __str__(self) -> str:
        return self.nombre

class EstadoSuscripcion(models.TextChoices):
    ACTIVA = 'activa', 'Activa'
    TRIAL = 'trial', 'Trial'
    PAUSADA = 'pausada', 'Pausada'
    CANCELADA = 'cancelada', 'Cancelada'
    EXPIRADA = 'expirada', 'Expirada'

class CicloSuscripcion(models.TextChoices):
    MENSUAL = 'mensual', 'Mensual'
    ANUAL = 'anual', 'Anual'

class Suscripcion(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='suscripciones'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='suscripciones'
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoSuscripcion,
        default=EstadoSuscripcion.TRIAL
    )
    ciclo = models.CharField(
        max_length=20,
        choices=CicloSuscripcion,
        default=CicloSuscripcion.MENSUAL
    )
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    auto_renovar = models.BooleanField(default=True)
    ultima_renovacion = models.DateTimeField(null=True, blank=True)
    cancelada_en = models.DateTimeField(null=True, blank=True)
    cancelada_por = models.CharField(max_length=100, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Suscripcion'
        verbose_name_plural = 'Suscripciones'
        constraints = [
            models.UniqueConstraint(
                fields=['empresa'],
                condition=Q(estado=EstadoSuscripcion.ACTIVA),
                name='unique_suscripcion_activa_por_empresa',
            )
        ]

    def __str__(self) -> str:
        return f"{self.empresa.nombre} - {self.plan.nombre}"

class SuscripcionCambio(models.Model):
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name='cambios')
    plan_anterior = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='cambios_desde')
    plan_nuevo = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='cambios_hacia')
    cambiado_en = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Cambio de suscripcion'
        verbose_name_plural = 'Cambios de suscripcion'

    def __str__(self) -> str:
        return f"{self.suscripcion.empresa.nombre}: {self.plan_anterior.nombre} -> {self.plan_nuevo.nombre}"
