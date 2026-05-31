from django.contrib import admin

from apps_privadas.notificaciones.models import Notificacion, Promocion


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'producto', 'estado', 'fecha_inicio', 'fecha_fin']
    search_fields = ['titulo', 'descripcion', 'producto__nombre']
    list_filter = ['estado', 'tipo_descuento']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'activa', 'ultimo_envio', 'fecha_actualizacion']
    search_fields = ['usuario__username', 'endpoint']
    list_filter = ['activa']
