"""
Datos artificiales para probar los módulos del sistema.
Estos datos se usan para测试 reportes y funcionalidades.
"""

from decimal import Decimal

# ===================== CLIENTES/USUARIOS =====================

CLIENTES = [
    {
        'username': 'juan_perez',
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': 'juan.perez@email.com',
        'password': 'password123'
    },
    {
        'username': 'maria_garcia',
        'nombre': 'María',
        'apellido': 'García',
        'email': 'maria.garcia@email.com',
        'password': 'password123'
    },
    {
        'username': 'carlos_lopez',
        'nombre': 'Carlos',
        'apellido': 'López',
        'email': 'carlos.lopez@email.com',
        'password': 'password123'
    },
    {
        'username': 'ana_rodriguez',
        'nombre': 'Ana',
        'apellido': 'Rodríguez',
        'email': 'ana.rodriguez@email.com',
        'password': 'password123'
    },
    {
        'username': 'luis_martinez',
        'nombre': 'Luis',
        'apellido': 'Martínez',
        'email': 'luis.martinez@email.com',
        'password': 'password123'
    },
]

# ===================== PROVEEDORES =====================

PROVEEDORES = [
    {
        'nombre': 'Distribuidora Tech',
        'direccion': 'Av. Industrial 123',
        'telefono': '3001234567'
    },
    {
        'nombre': 'Hogar Express',
        'direccion': 'Calle Commerce 456',
        'telefono': '3002345678'
    },
    {
        'nombre': 'Deportes Pro',
        'direccion': 'Blvd. Deportivo 789',
        'telefono': '3003456789'
    },
    {
        'nombre': 'Electro Supply',
        'direccion': 'Zona Industrial 101',
        'telefono': '3004567890'
    },
]

# ===================== CATEGORIAS =====================

CATEGORIAS = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Juguetes']

# ===================== MARCAS =====================

MARCAS = ['Samsung', 'Nike', 'Sony', 'Adidas']

# ===================== PRODUCTOS =====================

PRODUCTOS = [
    {
        'nombre': 'TV LED 40"',
        'descripcion': 'Televisor de 40 pulgadas Full HD con HDMI',
        'categoria': 'Electrónica',
        'marca': 'Samsung'
    },
    {
        'nombre': 'Smartphone Galaxy',
        'descripcion': 'Teléfono Android con cámara de 48MP',
        'categoria': 'Electrónica',
        'marca': 'Samsung'
    },
    {
        'nombre': 'Audífonos Wireless',
        'descripcion': 'Audífonos bluetooth con cancelación de ruido',
        'categoria': 'Electrónica',
        'marca': 'Sony'
    },
    {
        'nombre': 'Camiseta Dri-Fit',
        'descripcion': 'Camiseta deportiva de tecnología Dri-Fit',
        'categoria': 'Ropa',
        'marca': 'Nike'
    },
    {
        'nombre': 'Pantalón Deportivo',
        'descripcion': 'Pantalón jogger con bolsillo lateral',
        'categoria': 'Ropa',
        'marca': 'Adidas'
    },
    {
        'nombre': 'Sartén Antiadherente',
        'descripcion': 'Sartén de 26cm con recubrimiento cerámico',
        'categoria': 'Hogar',
        'marca': None
    },
    {
        'nombre': 'Juego de Ollas',
        'descripcion': 'Set de 5 piezas de acero inoxidable',
        'categoria': 'Hogar',
        'marca': None
    },
    {
        'nombre': 'Balón Fútbol',
        'descripcion': 'Balón oficial tamaño 5',
        'categoria': 'Deportes',
        'marca': None
    },
    {
        'nombre': 'Zapatillas Running',
        'descripcion': 'Zapatillas para correr con amortiguación',
        'categoria': 'Deportes',
        'marca': 'Adidas'
    },
    {
        'nombre': 'Robot de Juguete',
        'descripcion': 'Robot interactivo para niños',
        'categoria': 'Juguetes',
        'marca': None
    },
]

# ===================== VARIANTES POR PRODUCTO =====================

# Configuración para generar variantes de cada producto
# (num_variantes, rango_precio, rango_cantidad)
VARIANTES_CONFIG = {
    'TV LED 40"': (3, (800, 1200), (5, 20)),
    'Smartphone Galaxy': (2, (1500, 2500), (10, 30)),
    'Audífonos Wireless': (2, (200, 500), (15, 40)),
    'Camiseta Dri-Fit': (3, (80, 150), (20, 50)),
    'Pantalón Deportivo': (2, (120, 200), (15, 40)),
    'Sartén Antiadherente': (1, (60, 100), (10, 30)),
    'Juego de Ollas': (1, (200, 350), (5, 15)),
    'Balón Fútbol': (2, (50, 120), (20, 60)),
    'Zapatillas Running': (3, (200, 400), (10, 30)),
    'Robot de Juguete': (2, (80, 150), (15, 35)),
}

# ===================== CONFIGURACIÓN DE VENTAS =====================

VENTAS_CONFIG = {
    'cantidad': 20,
    'tipos': ['presencial', 'digital'],
    'tipos_pesos': [60, 40],  # 60% presencial, 40% digital
    'estados': ['completado', 'pendiente', 'cancelado'],
    'estados_pesos': [70, 20, 10],  # 70% completado, 20% pendiente, 10% cancelado
    'dias_atras_min': 1,
    'dias_atras_max': 30,
    'detalles_por_venta_min': 1,
    'detalles_por_venta_max': 4,
    'cantidad_por_detalle_min': 1,
    'cantidad_por_detalle_max': 5,
}

# ===================== CONFIGURACIÓN DE COMPRAS =====================

COMPRAS_CONFIG = {
    'cantidad': 10,
    'dias_atras_min': 1,
    'dias_atras_max': 60,
    'detalles_por_compra_min': 1,
    'detalles_por_compra_max': 4,
    'cantidad_por_detalle_min': 5,
    'cantidad_por_detalle_max': 20,
}