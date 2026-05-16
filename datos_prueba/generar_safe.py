#!/usr/bin/env python
"""
Script para generar datos artificiales de prueba para el tenant "tienda_amiga".
Usa los datos definidos en datos.py para poblar la base de datos.

Uso: python datos_prueba/generar.py
"""

import os
import sys
import django

# Configurar Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tienda.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from datos_prueba.datos import (
    CLIENTES, PROVEEDORES, CATEGORIAS, MARCAS, PRODUCTOS,
    VARIANTES_CONFIG, VENTAS_CONFIG, COMPRAS_CONFIG
)

from django.db import connection
from apps_publicas.empresas.models import Empresa
from apps_privadas.seguridad.models.usuario import Usuario
from apps_privadas.inventario.models import Categoria, Marca, Producto, VarianteProducto
from apps_privadas.compras.models import Proveedor, Compra, DetalleCompra
from apps_privadas.venta.models import Venta, DetalleVenta


def activar_tenant(nombre_schema):
    """Activa el schema del tenant especificado."""
    try:
        empresa = Empresa.objects.get(schema_name=nombre_schema)
        connection.set_tenant(empresa)
        print(f"[OK] Tenant '{nombre_schema}' activado")
        return empresa
    except Empresa.DoesNotExist:
        print(f"[ERROR] No se encontró el tenant '{nombre_schema}'")
        return None


def limpiar_todos_los_datos():
    """Elimina todos los datos existentes en orden correcto (por ForeignKey)."""
    print("Limpiando datos existentes...")
    try:
        DetalleVenta.objects.all().delete()
        Venta.objects.all().delete()
    except Exception:
        pass
    
    try:
        DetalleCompra.objects.all().delete()
        Compra.objects.all().delete()
    except Exception:
        pass
    
    try:
        VarianteProducto.objects.all().delete()
        Producto.objects.all().delete()
        Marca.objects.all().delete()
        Categoria.objects.all().delete()
    except Exception:
        pass
    
    try:
        Proveedor.objects.all().delete()
    except Exception:
        pass
    
    print("[OK] Datos limpiados\n")


def generar_clientes():
    """Genera usuarios/clientes para las ventas."""
    print("Generando clientes...")
    clientes = []
    
    for data in CLIENTES:
        usuario, created = Usuario.objects.get_or_create(
            username=data['username'],
            defaults={
                'nombre': data['nombre'],
                'apellido': data['apellido'],
                'email': data['email'],
                'is_active': True
            }
        )
        if created:
            usuario.set_password(data['password'])
            usuario.save()
        clientes.append(usuario)
    
    print(f"[OK] {len(clientes)} clientes creados")
    return clientes


def generar_proveedores():
    """Genera proveedores para las compras."""
    print("Generando proveedores...")
    proveedores = []
    
    for data in PROVEEDORES:
        prov, _ = Proveedor.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'direccion': data['direccion'],
                'telefono': data['telefono']
            }
        )
        proveedores.append(prov)
    
    print(f"[OK] {len(proveedores)} proveedores creados")
    return proveedores


def generar_categorias():
    """Genera categorías."""
    print("Generando categorías...")
    categorias = []
    
    for nombre in CATEGORIAS:
        cat, _ = Categoria.objects.get_or_create(nombre=nombre)
        categorias.append(cat)
    
    print(f"[OK] {len(categorias)} categorías creadas")
    return categorias


def generar_marcas():
    """Genera marcas."""
    print("Generando marcas...")
    marcas = []
    
    for nombre in MARCAS:
        marca, _ = Marca.objects.get_or_create(nombre=nombre)
        marcas.append(marca)
    
    # Crear marca "Sin Marca" para productos sin marca
    marca_sin_nombre, _ = Marca.objects.get_or_create(nombre='Sin Marca')
    
    print(f"[OK] {len(marcas)} marcas creadas + 1 genérica")
    return marcas, marca_sin_nombre


def generar_productos(categorias, marcas, marca_sin_nombre):
    """Genera productos."""
    print("Generando productos...")
    productos = []
    
    for data in PRODUCTOS:
        cat = next((c for c in categorias if c.nombre == data['categoria']), None)
        marca = next((m for m in marcas if m.nombre == data['marca']), None)
        if not marca:
            marca = marca_sin_nombre
        
        prod, _ = Producto.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'descripcion': data['descripcion'],
                'activo': True,
                'categoria': cat,
                'marca': marca
            }
        )
        productos.append(prod)
    
    print(f"[OK] {len(productos)} productos creados")
    return productos


def generar_variantes(productos):
    """Genera variantes para cada producto."""
    print("Generando variantes...")
    variantes = []
    
    for prod in productos:
        config = VARIANTES_CONFIG.get(prod.nombre, (2, (100, 500), (10, 30)))
        num_variantes, precio_range, cantidad_range = config
        
        for i in range(num_variantes):
            # Generar SKU único
            sku_base = prod.nombre[:3].upper().replace('"', '')
            sku = f"{sku_base}-{prod.id}-{i+1}"
            
            # Generar datos aleatorios
            precio = Decimal(random.randint(precio_range[0], precio_range[1]))
            cantidad = random.randint(cantidad_range[0], cantidad_range[1])
            costo_ponderado = precio * Decimal('0.7')
            
            variante, _ = VarianteProducto.objects.get_or_create(
                sku=sku,
                defaults={
                    'precio': precio,
                    'cantidad': cantidad,
                    'costo_ponderado': costo_ponderado.quantize(Decimal('0.01')),
                    'limite_cantidad': 10,
                    'producto': prod
                }
            )
            variantes.append(variante)
    
    print(f"[OK] {len(variantes)} variantes creadas")
    return variantes


def generar_ventas(variantes, clientes):
    """Genera ventas con detalles."""
    print("Generando ventas...")
    ventas = []
    
    config = VENTAS_CONFIG
    
    for i in range(config['cantidad']):
        dias_atras = random.randint(config['dias_atras_min'], config['dias_atras_max'])
        fecha = timezone.now() - timedelta(days=dias_atras)
        
        tipo = random.choices(config['tipos'], weights=config['tipos_pesos'])[0]
        estado = random.choices(config['estados'], weights=config['estados_pesos'])[0]
        
        venta = Venta.objects.create(
            tipo=tipo,
            estado=estado,
            fecha=fecha,
            precio_total=Decimal('0'),
            usuario=random.choice(clientes)
        )
        
        # Crear detalles
        num_detalles = random.randint(config['detalles_por_venta_min'], config['detalles_por_venta_max'])
        variantes_sample = random.sample(variantes, min(num_detalles, len(variantes)))
        
        precio_total = Decimal('0')
        for var in variantes_sample:
            cantidad = random.randint(config['cantidad_por_detalle_min'], config['cantidad_por_detalle_max'])
            precio_unitario = var.precio
            precio_subtotal = cantidad * precio_unitario
            precio_total += precio_subtotal
            
            DetalleVenta.objects.create(
                cantidad=cantidad,
                precio_subtotal=precio_subtotal,
                precio_unitario=precio_unitario,
                variante_producto=var,
                venta=venta
            )
        
        venta.precio_total = precio_total
        venta.save()
        ventas.append(venta)
    
    print(f"[OK] {len(ventas)} ventas creadas con sus detalles")
    return ventas


def generar_compras(variantes, proveedores):
    """Genera compras con detalles."""
    print("Generando compras...")
    compras = []
    
    config = COMPRAS_CONFIG
    
    for i in range(config['cantidad']):
        dias_atras = random.randint(config['dias_atras_min'], config['dias_atras_max'])
        fecha = timezone.now() - timedelta(days=dias_atras)
        
        compra = Compra.objects.create(
            fecha=fecha,
            total=Decimal('0'),
            proveedor=random.choice(proveedores)
        )
        
        # Crear detalles
        num_detalles = random.randint(config['detalles_por_compra_min'], config['detalles_por_compra_max'])
        variantes_sample = random.sample(variantes, min(num_detalles, len(variantes)))
        
        total = Decimal('0')
        for var in variantes_sample:
            cantidad = random.randint(config['cantidad_por_detalle_min'], config['cantidad_por_detalle_max'])
            costo_unitario = var.costo_ponderado
            costo_subtotal = cantidad * costo_unitario
            total += costo_subtotal
            
            DetalleCompra.objects.create(
                cantidad=cantidad,
                costo_subtotal=costo_subtotal,
                costo_unitario=costo_unitario,
                variante_producto=var,
                compra=compra
            )
        
        compra.total = total
        compra.save()
        compras.append(compra)
    
    print(f"[OK] {len(compras)} compras creadas con sus detalles")
    return compras


def run():
    """Ejecuta la generación de todos los datos."""
    print("="*60)
    print("GENERANDO DATOS DE PRUEBA PARA 'tienda_amiga'")
    print("="*60 + "\n")
    
    # Activar el tenant
    print(">>> Conectando al tenant 'tienda_amiga'...")
    empresa = activar_tenant('tienda_amiga')
    if not empresa:
        print("\n[ERROR] No se pudo conectar al tenant. Asegúrate de que 'tienda_amiga' exista.")
        print("   Ejecuta: python create_tenant.py")
        return
    
    # Limpiar datos existentes
    print("\n>>> Paso 1: Limpiando datos existentes...")
    limpiar_todos_los_datos()
    
    # Generar datos base
    print("\n>>> Paso 2: Generando clientes...")
    clientes = generar_clientes()
    
    print("\n>>> Paso 3: Generando proveedores...")
    proveedores = generar_proveedores()
    
    print("\n>>> Paso 4: Generando categorías...")
    categorias = generar_categorias()
    
    print("\n>>> Paso 5: Generando marcas...")
    marcas, marca_sin_nombre = generar_marcas()
    
    print("\n>>> Paso 6: Generando productos...")
    productos = generar_productos(categorias, marcas, marca_sin_nombre)
    
    print("\n>>> Paso 7: Generando variantes...")
    variantes = generar_variantes(productos)
    
    # Generar transacciones
    print("\n>>> Paso 8: Generando ventas...")
    ventas = generar_ventas(variantes, clientes)
    
    print("\n>>> Paso 9: Generando compras...")
    compras = generar_compras(variantes, proveedores)
    
    # Resumen
    print("\n" + "="*60)
    print("[OK] DATOS GENERADOS EXITOSAMENTE")
    print("="*60)
    print(f"""
[STATS] Resumen de datos creados:

   Clientes:      {len(clientes)}
   Proveedores:   {len(proveedores)}
   Categorías:    {len(categorias)}
   Marcas:        {len(marcas)}
   Productos:     {len(productos)}
   Variantes:     {len(variantes)}
   Ventas:        {len(ventas)}
   Compras:       {len(compras)}

[NOTES] Endpoints disponibles para probar:

   GET /api/categorias/
   GET /api/marcas/
   GET /api/productos/
   GET /api/variantes/
   GET /api/ventas/
   GET /api/proveedores/
   GET /api/compras/

[KEYS] Usuarios para login (password: password123):
   juan_perez, maria_garcia, carlos_lopez, ana_rodriguez, luis_martinez
""")


if __name__ == '__main__':
    run()
