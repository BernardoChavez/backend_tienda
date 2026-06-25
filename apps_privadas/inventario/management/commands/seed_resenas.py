import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

from apps_privadas.inventario.models import Producto
from apps_privadas.inventario.models.resena import Resena
from apps_privadas.venta.models import DetalleVenta

Usuario = get_user_model()

COMENTARIOS = [
    'Excelente calidad, muy recomendado.',
    'Llegó en perfectas condiciones, muy contento con la compra.',
    'Buena relación calidad-precio.',
    'El producto es exactamente como se describe, muy satisfecho.',
    'Material resistente y acabado impecable.',
    'Muy buen producto, lo recomiendo a todos.',
    'Superó mis expectativas, quedó perfecto en mi sala.',
    'Buen producto aunque la entrega tardó un poco.',
    'Calidad aceptable para el precio.',
    'El diseño es moderno y encaja bien con mi decoración.',
    'Producto sólido y bien terminado.',
    'Me gustó bastante, repetiría la compra.',
    'Buena compra, cumple con lo prometido.',
    'La calidad es buena pero el precio podría ser mejor.',
    'Muy satisfecho con la compra, lo recomiendo.',
    'Producto bonito pero el armado fue un poco complicado.',
    'Durabilidad excelente, lleva meses y sigue como nuevo.',
    'Buena compra, el material es de calidad.',
    'Cumple su función perfectamente.',
    'Muy bonito, exactamente lo que buscaba.',
]


class Command(BaseCommand):
    help = (
        'Genera reseñas ficticias para productos comprados. '
        'Requiere que seed_muebles ya haya sido ejecutado. '
        'Usar: python manage.py seed_resenas --schema <nombre_schema>'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema', type=str, default=None,
            help='Schema del tenant donde se insertarán los datos.'
        )
        parser.add_argument(
            '--max-por-producto', type=int, default=10,
            help='Máximo de reseñas por producto (default: 10).'
        )

    def handle(self, *args, **options):
        schema = options['schema']
        if schema:
            connection.set_schema(schema)
            self.stdout.write(f'Schema activo: {schema}')

        max_por_producto = options['max_por_producto']

        productos = list(Producto.objects.filter(activo=True))
        if not productos:
            self.stdout.write(self.style.WARNING('No hay productos. Ejecuta seed_muebles primero.'))
            return

        total_creadas = 0
        total_omitidas = 0

        for producto in productos:
            # Usuarios que compraron este producto en una venta completada
            usuarios_compradores = list(
                Usuario.objects.filter(
                    ventas__estado='completado',
                    ventas__detalles__variante_producto__producto=producto,
                ).distinct()
            )

            if not usuarios_compradores:
                continue

            candidatos = random.sample(
                usuarios_compradores,
                min(max_por_producto, len(usuarios_compradores))
            )

            for usuario in candidatos:
                _, creada = Resena.objects.get_or_create(
                    usuario=usuario,
                    producto=producto,
                    defaults={
                        'calificacion': random.choices(
                            [1, 2, 3, 4, 5],
                            weights=[2, 5, 15, 40, 38]
                        )[0],
                        'comentario': random.choice(COMENTARIOS),
                    }
                )
                if creada:
                    total_creadas += 1
                else:
                    total_omitidas += 1

            self.stdout.write(f'  {producto.nombre}: {len(candidatos)} reseñas procesadas')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seed reseñas completado: {total_creadas} creadas, {total_omitidas} ya existían.'
        ))