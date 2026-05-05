from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Modelo personalizado de Usuario heredando de AbstractUser.
    
    Hereda todos los campos y métodos de AbstractUser:
    - id, username, password, is_staff, is_superuser, is_active, groups, etc.
    
    Campos adicionales (opcionales):
    - nombre: Nombre del usuario
    - apellido: Apellido del usuario
    - fecha_nacimiento: Fecha de nacimiento
    - email: Email del usuario (heredado, se hace opcional)
    """
    
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    # Hacer email opcional (por defecto en AbstractUser es requerido)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.username})" if self.nombre else self.username
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}".strip() if self.nombre else ""


class CodigoRecuperacion(models.Model):
    """
    Almacena los códigos temporales para recuperación de contraseña.
    Expira a los 15 minutos de su creación.
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
        verbose_name = 'Código de Recuperación'
        verbose_name_plural = 'Códigos de Recuperación'

    def esta_vigente(self):
        return not self.usado and timezone.now() < self.expira_en

    def __str__(self):
        return f"{self.usuario.username} - {self.codigo}"
