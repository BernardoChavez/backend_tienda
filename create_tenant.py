#!/usr/bin/env python
"""
Script para crear un nuevo tenant (esquema y empresa) en django-tenants
Uso: python manage.py shell < create_tenant.py
O: python create_tenant.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tienda.settings')
django.setup()

from apps_publicas.empresas.models import Empresa, Dominio

# Crear la empresa "Tienda Amiga"
empresa = Empresa.objects.create(
    nombre='Tienda Amiga',
    schema_name='tienda_amiga',  # django-tenants usa schema_name
    correo='info@tienda-amiga.com',
    is_active=True
)

print(f"[OK] Empresa creada: {empresa.nombre} (ID: {empresa.id})")
print(f"  Schema: {empresa.schema_name}")

# Crear el dominio para la empresa
dominio = Dominio.objects.create(
    domain='tienda-amiga.localhost',
    tenant=empresa,
    is_primary=True
)

print(f"[OK] Dominio creado: {dominio.domain}")
print(f"\nTienda Amiga está lista para usar en: http://tienda-amiga.localhost")



