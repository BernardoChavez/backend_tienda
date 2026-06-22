#!/usr/bin/env python
"""
Script para crear o reutilizar el tenant Tienda Amiga.

Uso:
    python create_tenant.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tienda.settings')
django.setup()

from apps_publicas.empresas.models import Dominio, Empresa


empresa, creada = Empresa.objects.get_or_create(
    schema_name='tienda_amiga',
    defaults={
        'nombre': 'Tienda Amiga',
        'correo': 'info@tienda-amiga.com',
        'is_active': True,
    },
)

if creada:
    print(f"[OK] Empresa creada: {empresa.nombre} (ID: {empresa.id})")
else:
    print(f"[OK] Empresa existente: {empresa.nombre} (ID: {empresa.id})")
print(f"  Schema: {empresa.schema_name}")

dominio, dominio_creado = Dominio.objects.get_or_create(
    domain='tienda-amiga.localhost',
    defaults={
        'tenant': empresa,
        'is_primary': True,
    },
)

if not dominio_creado and dominio.tenant_id != empresa.id:
    dominio.tenant = empresa
    dominio.is_primary = True
    dominio.save(update_fields=['tenant', 'is_primary'])

print(f"[OK] Dominio {'creado' if dominio_creado else 'existente'}: {dominio.domain}")
print("\nTienda Amiga esta lista para usar en: http://tienda-amiga.localhost")
