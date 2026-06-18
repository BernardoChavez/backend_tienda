import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

from apps_privadas.compras.models import Compra, DetalleCompra, Proveedor
from apps_privadas.inventario.models import Categoria, Marca, Producto, VarianteProducto
from apps_privadas.venta.models import DetalleVenta, Venta

Usuario = get_user_model()

# Multiplicador de ventas por mes (1.0 = mes promedio)
# Patrón estacional para tienda de muebles en Bolivia
ESTACIONALIDAD = {
    1: 0.85, 2: 0.80, 3: 1.00, 4: 0.95,
    5: 0.90, 6: 1.10, 7: 1.30, 8: 1.05,
    9: 0.95, 10: 1.05, 11: 1.25, 12: 1.50,
}

CATEGORIAS = ['Salas', 'Dormitorios', 'Comedor', 'Oficina', 'Exterior']

MARCAS = ['Madeform', 'Ropimex', 'Modena', 'NovaHome']

PROVEEDORES = [
    {'nombre': 'MaderaSur S.A.',       'direccion': 'Av. Blanco Galindo Km 5', 'telefono': '4-4521100'},
    {'nombre': 'ImportMuebles Bolivia', 'direccion': 'Parque Industrial Cbba',  'telefono': '4-4389200'},
    {'nombre': 'Diseños Andinos Ltda.', 'direccion': 'Calle Calama 345, Cbba',  'telefono': '4-4112300'},
]

# (nombre, descripcion, categoria, marca)
PRODUCTOS = [
    ('Sofá 3 Plazas Milano',       'Sofá tapizado en tela resistente para sala',          'Salas',      'Madeform'),
    ('Sofá 2 Plazas Roma',         'Sofá compacto ideal para espacios pequeños',           'Salas',      'Modena'),
    ('Sillón Reclinable Comfort',  'Sillón reclinable con reposapiés integrado',           'Salas',      'NovaHome'),
    ('Mesa de Centro Oslo',        'Mesa de centro con vidrio templado y madera',          'Salas',      'Ropimex'),
    ('Estante Modular Cubic',      'Estante de 5 niveles ensamblable',                     'Salas',      'Madeform'),
    ('Cama 2 Plazas Sevilla',      'Cama con cabecera acolchada e incluye somier',         'Dormitorios','Modena'),
    ('Cama 1.5 Plazas Valencia',   'Cama individual con cajones de almacenamiento',        'Dormitorios','Madeform'),
    ('Ropero 4 Puertas Harmony',   'Ropero con espejo interior y gavetas',                 'Dormitorios','NovaHome'),
    ('Cómoda 5 Cajones Nordic',    'Cómoda de madera con tirador metálico',                'Dormitorios','Ropimex'),
    ('Mesa Comedor 6p Toscana',    'Mesa rectangular de madera sólida para 6 personas',    'Comedor',    'Madeform'),
    ('Mesa Comedor 4p Siena',      'Mesa cuadrada con patas de metal para 4 personas',     'Comedor',    'Modena'),
    ('Silla Comedor Venecia',      'Silla con asiento tapizado y patas de madera',         'Comedor',    'Ropimex'),
    ('Vitrina Comedor Classic',    'Vitrina con puertas de vidrio y luz interior',          'Comedor',    'NovaHome'),
    ('Escritorio Ejecutivo Pro',   'Escritorio en L con cajonera integrada',               'Oficina',    'Madeform'),
    ('Silla Ejecutiva ErgoMax',    'Silla ergonómica con soporte lumbar regulable',         'Oficina',    'NovaHome'),
    ('Librero 5 Niveles Scholar',  'Estante para libros con refuerzo metálico',            'Oficina',    'Modena'),
    ('Mesa Auxiliar Flex',         'Mesa pequeña multiuso con ruedas',                     'Oficina',    'Ropimex'),
    ('Juego de Jardín Tropical',   'Set mesa + 4 sillas de ratán sintético',               'Exterior',   'NovaHome'),
    ('Mesa Exterior Clima',        'Mesa resistente a intemperie de aluminio',              'Exterior',   'Modena'),
    ('Silla Exterior Urban',       'Silla plegable de aluminio con textilene',             'Exterior',   'Ropimex'),
]

# (sufijo_sku, precio_venta, costo, limite_minimo)
VARIANTES_CONFIG = {
    'Sofá 3 Plazas Milano':      [('GRS', 3200, 1800, 3), ('BEI', 3400, 1900, 3), ('AZL', 3600, 2000, 2)],
    'Sofá 2 Plazas Roma':        [('GRS', 2200, 1200, 3), ('CAF', 2400, 1300, 2)],
    'Sillón Reclinable Comfort': [('NEG', 1800, 1000, 2), ('GRS', 1900, 1050, 2)],
    'Mesa de Centro Oslo':       [('ROB', 850,   480, 3), ('NEG', 950,   530, 2)],
    'Estante Modular Cubic':     [('BLA', 620,   340, 4), ('WEN', 680,   370, 3)],
    'Cama 2 Plazas Sevilla':     [('GRS', 2800, 1600, 2), ('BLA', 3000, 1700, 2)],
    'Cama 1.5 Plazas Valencia':  [('BLA', 1800, 1000, 3), ('GRS', 1900, 1050, 2)],
    'Ropero 4 Puertas Harmony':  [('WEN', 3500, 2000, 2), ('BLA', 3700, 2100, 2)],
    'Cómoda 5 Cajones Nordic':   [('BLA', 1200,  680, 3), ('NEG', 1350,  750, 2)],
    'Mesa Comedor 6p Toscana':   [('ROB', 4200, 2400, 2), ('NEG', 4500, 2600, 2)],
    'Mesa Comedor 4p Siena':     [('BLA', 2600, 1500, 3), ('NEG', 2800, 1600, 2)],
    'Silla Comedor Venecia':     [('GRS', 480,   260, 6), ('BEI', 520,   280, 5), ('NEG', 500, 270, 5)],
    'Vitrina Comedor Classic':   [('BLA', 2900, 1650, 2), ('ROB', 3100, 1750, 2)],
    'Escritorio Ejecutivo Pro':  [('NEG', 2400, 1350, 2), ('ROB', 2600, 1450, 2)],
    'Silla Ejecutiva ErgoMax':   [('NEG', 1600,  900, 3), ('GRS', 1700,  950, 2)],
    'Librero 5 Niveles Scholar': [('BLA', 890,   490, 3), ('ROB', 950,   520, 2)],
    'Mesa Auxiliar Flex':        [('NEG', 420,   230, 4), ('BLA', 450,   245, 3)],
    'Juego de Jardín Tropical':  [('CAF', 3800, 2100, 2), ('GRS', 4000, 2200, 2)],
    'Mesa Exterior Clima':       [('GRS', 1100,  620, 3), ('NEG', 1200,  670, 2)],
    'Silla Exterior Urban':      [('GRS', 380,   210, 5), ('NEG', 420,   230, 4)],
}

CLIENTES = [
    ('juan_perez',     'Juan',     'Pérez',      'juan.perez@mail.com'),
    ('maria_garcia',   'María',    'García',     'maria.garcia@mail.com'),
    ('carlos_lopez',   'Carlos',   'López',      'carlos.lopez@mail.com'),
    ('ana_rodriguez',  'Ana',      'Rodríguez',  'ana.rodriguez@mail.com'),
    ('luis_martinez',  'Luis',     'Martínez',   'luis.martinez@mail.com'),
    ('sofia_torrez',   'Sofía',    'Torrez',     'sofia.torrez@mail.com'),
    ('diego_mamani',   'Diego',    'Mamani',     'diego.mamani@mail.com'),
    ('claudia_rios',   'Claudia',  'Ríos',       'claudia.rios@mail.com'),
    ('roberto_vega',   'Roberto',  'Vega',       'roberto.vega@mail.com'),
    ('patricia_leon',  'Patricia', 'León',       'patricia.leon@mail.com'),
    ('andres_flores',  'Andrés',   'Flores',     'andres.flores@mail.com'),
    ('carmen_choque',  'Carmen',   'Choque',     'carmen.choque@mail.com'),
    ('miguel_quispe',  'Miguel',   'Quispe',     'miguel.quispe@mail.com'),
    ('laura_condori',  'Laura',    'Condori',    'laura.condori@mail.com'),
    ('jose_alvarado',  'José',     'Alvarado',   'jose.alvarado@mail.com'),
]


class Command(BaseCommand):
    help = (
        'Genera datos ficticios consistentes de mueblería para entrenamiento del modelo ML. '
        'Usar: python manage.py seed_muebles --schema <nombre_schema>'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema', type=str, default=None,
            help='Schema del tenant donde se insertarán los datos.'
        )
        parser.add_argument(
            '--ventas-por-mes', type=int, default=500,
            help='Ventas base por mes antes de aplicar estacionalidad (default: 500).'
        )
        parser.add_argument(
            '--meses', type=int, default=18,
            help='Cuántos meses de historial generar contando hacia atrás desde hoy (default: 18).'
        )

    def handle(self, *args, **options):
        schema = options['schema']
        if schema:
            connection.set_schema(schema)
            self.stdout.write(f'Schema activo: {schema}')

        ventas_base = options['ventas_por_mes']
        meses = options['meses']

        self.stdout.write('Creando catálogo base...')
        categorias  = self._crear_categorias()
        marcas      = self._crear_marcas()
        proveedores = self._crear_proveedores()
        usuarios    = self._crear_usuarios()
        productos   = self._crear_productos(categorias, marcas)
        variantes   = self._crear_variantes(productos)

        self.stdout.write(f'  {len(variantes)} variantes creadas.')

        # stock en memoria: {variante_id: cantidad_disponible}
        stock = {v.id: 0 for v in variantes}

        self.stdout.write('Generando historial de compras y ventas...')
        hoy = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        inicio = hoy - timedelta(days=meses * 30)

        total_ventas = 0
        total_detalles = 0

        for offset_mes in range(meses):
            fecha_mes = inicio + timedelta(days=offset_mes * 30)
            mes = fecha_mes.month

            # --- COMPRAS al inicio de cada mes ---
            self._crear_compras_mes(variantes, proveedores, fecha_mes, stock)

            # --- VENTAS durante el mes ---
            cantidad_ventas = int(ventas_base * ESTACIONALIDAD.get(mes, 1.0))
            detalles_mes = self._crear_ventas_mes(
                variantes, usuarios, fecha_mes, cantidad_ventas, stock
            )
            total_ventas += cantidad_ventas
            total_detalles += detalles_mes

            self.stdout.write(
                f'  {fecha_mes.strftime("%Y-%m")}: '
                f'{cantidad_ventas} ventas, {detalles_mes} detalles'
            )

        # Establecer stock final realista para cada variante
        # (independiente de la simulación, para reflejar inventario actual de la tienda)
        self.stdout.write('Estableciendo stock final en base de datos...')
        for variante in variantes:
            # Stock entre 2× y 6× el límite mínimo configurado, mínimo 5 unidades
            stock_final = random.randint(
                max(5, variante.limite_cantidad * 2),
                max(10, variante.limite_cantidad * 6),
            )
            self.stdout.write(f'  {variante.sku}: {stock_final} unidades')
            VarianteProducto.objects.filter(pk=variante.pk).update(cantidad=stock_final)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seed completado: {total_ventas} ventas, {total_detalles} detalles de venta.'
        ))

    # ------------------------------------------------------------------ #

    def _crear_categorias(self):
        result = {}
        for nombre in CATEGORIAS:
            obj, _ = Categoria.objects.get_or_create(nombre=nombre)
            result[nombre] = obj
        return result

    def _crear_marcas(self):
        result = {}
        for nombre in MARCAS:
            obj, _ = Marca.objects.get_or_create(nombre=nombre)
            result[nombre] = obj
        return result

    def _crear_proveedores(self):
        result = []
        for data in PROVEEDORES:
            obj, _ = Proveedor.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'direccion': data['direccion'], 'telefono': data['telefono']}
            )
            result.append(obj)
        return result

    def _crear_usuarios(self):
        result = []
        for username, nombre, apellido, email in CLIENTES:
            obj, created = Usuario.objects.get_or_create(
                username=username,
                defaults={'nombre': nombre, 'apellido': apellido, 'email': email}
            )
            if created:
                obj.set_password('password123')
                obj.save()
            result.append(obj)

        # Usar superusuario si existe, para no requerir admin creado
        admin = Usuario.objects.filter(is_superuser=True).first()
        if admin and admin not in result:
            result.append(admin)

        return result

    def _crear_productos(self, categorias, marcas):
        result = {}
        for nombre, descripcion, cat_nombre, marca_nombre in PRODUCTOS:
            obj, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'categoria': categorias[cat_nombre],
                    'marca': marcas[marca_nombre],
                    'activo': True,
                }
            )
            result[nombre] = obj
        return result

    def _crear_variantes(self, productos):
        variantes = []
        for nombre_prod, configs in VARIANTES_CONFIG.items():
            producto = productos[nombre_prod]
            prefijo = ''.join(w[0] for w in nombre_prod.split()[:3]).upper()
            for sufijo, precio, costo, limite in configs:
                sku = f'{prefijo}-{sufijo}'
                obj, _ = VarianteProducto.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'precio': Decimal(precio),
                        'costo_ponderado': Decimal(costo),
                        'limite_cantidad': limite,
                        'cantidad': 0,
                        'producto': producto,
                    }
                )
                variantes.append(obj)
        return variantes

    def _crear_compras_mes(self, variantes, proveedores, fecha_mes, stock):
        """Crea una compra al inicio del mes para reponer stock de cada variante."""
        proveedor = random.choice(proveedores)
        fecha_compra = fecha_mes.replace(day=random.randint(1, 5))

        compra = Compra.objects.create(proveedor=proveedor, total=Decimal('0'))
        Compra.objects.filter(pk=compra.pk).update(fecha=fecha_compra)

        detalles = []
        total = Decimal('0')

        # Comprar para todos los productos, cantidad variable
        for variante in variantes:
            cantidad = random.randint(45, 55)
            costo_u = variante.costo_ponderado
            subtotal = costo_u * cantidad
            detalles.append(DetalleCompra(
                compra=compra,
                variante_producto=variante,
                cantidad=cantidad,
                costo_unitario=costo_u,
                costo_subtotal=subtotal,
            ))
            stock[variante.id] += cantidad
            total += subtotal

        DetalleCompra.objects.bulk_create(detalles)
        Compra.objects.filter(pk=compra.pk).update(total=total)

    def _crear_ventas_mes(self, variantes, usuarios, fecha_mes, cantidad_ventas, stock):
        """Crea ventas distribuidas aleatoriamente durante el mes."""
        dias_en_mes = 28
        detalles_creados = 0

        for _ in range(cantidad_ventas):
            dia = random.randint(1, dias_en_mes)
            hora = random.randint(8, 20)
            minuto = random.randint(0, 59)
            fecha_venta = fecha_mes.replace(day=dia, hour=hora, minute=minuto)

            usuario = random.choice(usuarios)
            tipo = random.choices(['digital', 'presencial'], weights=[60, 40])[0]

            venta = Venta.objects.create(
                tipo=tipo,
                estado='completado',
                precio_total=Decimal('0'),
                usuario=usuario,
            )
            Venta.objects.filter(pk=venta.pk).update(fecha=fecha_venta)

            # 1 a 3 productos por venta
            num_items = random.choices([1, 2, 3], weights=[55, 35, 10])[0]
            variantes_disponibles = [v for v in variantes if stock[v.id] >= 1]

            if not variantes_disponibles:
                venta.delete()
                continue

            seleccionadas = random.sample(
                variantes_disponibles,
                min(num_items, len(variantes_disponibles))
            )

            detalles = []
            total = Decimal('0')

            for variante in seleccionadas:
                max_cant = min(stock[variante.id], 3)
                if max_cant < 1:
                    continue
                cantidad = random.randint(1, max_cant)
                precio_u = variante.precio
                subtotal = precio_u * cantidad

                detalles.append(DetalleVenta(
                    venta=venta,
                    variante_producto=variante,
                    cantidad=cantidad,
                    precio_unitario=precio_u,
                    precio_subtotal=subtotal,
                ))
                stock[variante.id] -= cantidad
                total += subtotal

            if not detalles:
                venta.delete()
                continue

            DetalleVenta.objects.bulk_create(detalles)
            Venta.objects.filter(pk=venta.pk).update(precio_total=total)
            detalles_creados += len(detalles)

        return detalles_creados