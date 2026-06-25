from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django_tenants.signals import post_schema_sync
from django_tenants.utils import schema_context

# (app_label, codename)
PERMISOS_CLIENTE = [
    # Catálogo - solo lectura
    ('inventario', 'view_categoria'),
    ('inventario', 'view_marca'),
    ('inventario', 'view_producto'),
    ('inventario', 'view_varianteproducto'),
    ('inventario', 'view_multimedio'),
    # Reseñas - CRUD completo
    ('inventario', 'add_resena'),
    ('inventario', 'view_resena'),
    ('inventario', 'change_resena'),
    ('inventario', 'delete_resena'),
    # Favoritos
    ('inventario', 'add_productofavorito'),
    ('inventario', 'view_productofavorito'),
    ('inventario', 'delete_productofavorito'),
    # Ventas - crear y consultar las propias
    ('venta', 'add_venta'),
    ('venta', 'view_venta'),
    ('venta', 'add_detalleventa'),
    ('venta', 'view_detalleventa'),
    # Carrito - CRUD completo
    ('carrito', 'add_carrito'),
    ('carrito', 'view_carrito'),
    ('carrito', 'change_carrito'),
    ('carrito', 'delete_carrito'),
    ('carrito', 'add_detallecarrito'),
    ('carrito', 'view_detallecarrito'),
    ('carrito', 'change_detallecarrito'),
    ('carrito', 'delete_detallecarrito'),
    # Notificaciones - solo lectura
    ('notificaciones', 'view_notificacion'),
]


@receiver(post_schema_sync)
def crear_grupos_iniciales(sender, tenant, **kwargs):
    if tenant.schema_name == 'public':
        return

    with schema_context(tenant.schema_name):
        grupo_cliente, creado = Group.objects.get_or_create(name='Cliente')

        permisos = []
        for app_label, codename in PERMISOS_CLIENTE:
            try:
                perm = Permission.objects.get(
                    codename=codename,
                    content_type__app_label=app_label,
                )
                permisos.append(perm)
            except Permission.DoesNotExist:
                print(f"  [WARN] Permiso no encontrado: {app_label}.{codename}")

        grupo_cliente.permissions.set(permisos)
        accion = 'creado' if creado else 'actualizado'
        print(f"OK Grupo 'Cliente' {accion} en schema '{tenant.schema_name}' con {len(permisos)} permisos")