from django.core.management.base import BaseCommand

from apps_publicas.empresas.models import Plan


class Command(BaseCommand):
    help = 'Puebla la base de datos con los planes de suscripcion para la plataforma SaaS'

    def handle(self, *args, **kwargs):
        planes_data = [
            {
                'nombre': 'Plan Trial',
                'descripcion': 'Prueba gratuita de 14 dias para experimentar con Realidad Aumentada y 3D en tus muebles.',
                'precio_mensual': 0.00,
                'precio_anual': 0.00,
                'activo': True,
                'limite_usuarios': 1,
                'limite_productos': 10,
                'limite_clientes': 10,
                'limite_proveedores': 2,
                'feature_realidad_aumentada': True,
                'feature_fotos_3d': True,
                'feature_reportes_dinamicos': True,
                'feature_backup_automatico': False,
            },
            {
                'nombre': 'Plan Basico',
                'descripcion': 'Ideal para carpinteros independientes o tiendas pequenas que inician su digitalizacion.',
                'precio_mensual': 29.00,
                'precio_anual': 290.00,
                'activo': True,
                'limite_usuarios': 2,
                'limite_productos': 50,
                'limite_clientes': 500,
                'limite_proveedores': 10,
                'feature_realidad_aumentada': False,
                'feature_fotos_3d': False,
                'feature_reportes_dinamicos': False,
                'feature_backup_automatico': True,
            },
            {
                'nombre': 'Plan Profesional',
                'descripcion': 'Para mueblerias establecidas. Incluye Realidad Aumentada para aumentar conversiones en tienda y online.',
                'precio_mensual': 89.00,
                'precio_anual': 890.00,
                'activo': True,
                'limite_usuarios': 10,
                'limite_productos': 500,
                'limite_clientes': 5000,
                'limite_proveedores': 50,
                'feature_realidad_aumentada': True,
                'feature_fotos_3d': False,
                'feature_reportes_dinamicos': True,
                'feature_backup_automatico': True,
            },
            {
                'nombre': 'Plan Premium',
                'descripcion': 'La experiencia omnicanal definitiva para fabricantes y grandes distribuidores de muebles.',
                'precio_mensual': 299.00,
                'precio_anual': 2990.00,
                'activo': True,
                'limite_usuarios': 0,
                'limite_productos': 0,
                'limite_clientes': 0,
                'limite_proveedores': 0,
                'feature_realidad_aumentada': True,
                'feature_fotos_3d': True,
                'feature_reportes_dinamicos': True,
                'feature_backup_automatico': True,
            },
        ]

        for plan_data in planes_data:
            plan, created = Plan.objects.update_or_create(
                nombre=plan_data['nombre'],
                defaults=plan_data,
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Plan "{plan.nombre}" creado exitosamente.'))
            else:
                self.stdout.write(self.style.WARNING(f'Plan "{plan.nombre}" actualizado.'))

        self.stdout.write(
            self.style.SUCCESS('\nTodos los planes han sido sembrados correctamente en la base de datos.')
        )
