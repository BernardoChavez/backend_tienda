from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps_privadas.seguridad.models.usuario import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario"""
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('nombre', 'apellido', 'fecha_nacimiento')
        }),
    )
    
    list_display = ('nombre_completo', 'username', 'email', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'nombre', 'apellido')
