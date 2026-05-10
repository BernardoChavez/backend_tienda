#!/usr/bin/env python
"""
Script para configurar el tenant Admin y los dominios públicos.
Crea la empresa "Admin" con dominios 127.0.0.1 y localhost.

Uso: python setup_admin_tenant.py

Este script:
1. Crea empresa "Admin" con schema_name='public'
2. Registra dominio 127.0.0.1 (principal)
3. Registra dominio localhost
4. Permite acceder a http://127.0.0.1:8000/admin/
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tienda.settings')
django.setup()

from apps_publicas.empresas.models import Empresa, Dominio


def setup_admin_tenant():
    """Crea el tenant Admin para el acceso público"""

    print("\n" + "="*60)
    print("--- CONFIGURACION DEL TENANT ADMIN ---")
    print("="*60 + "\n")

    try:
        # Verificar si ya existe
        empresa_admin = Empresa.objects.filter(schema_name='public').first()

        if empresa_admin:
            print("[!] El tenant Admin ya existe.\n")
            print(f"  Nombre: {empresa_admin.nombre}")
            print(f"  Schema: {empresa_admin.schema_name}")
            print(f"  Email: {empresa_admin.correo}\n")

            # Verificar dominios
            dominios = Dominio.objects.filter(tenant=empresa_admin)
            print("  Dominios registrados:")
            for dominio in dominios:
                print(f"    - {dominio.domain}")
            print()

            return True

        # Crear la empresa Admin
        print("[...] Creando empresa Admin...")
        empresa_admin = Empresa.objects.create(
            nombre='Admin',
            schema_name='public',
            correo='admin@localhost.com',
            is_active=True
        )

        print(f"[OK] Empresa creada: {empresa_admin.nombre} (ID: {empresa_admin.id})")
        print(f"  Schema: {empresa_admin.schema_name}\n")

        # Crear dominio 127.0.0.1
        print("[...] Registrando dominio 127.0.0.1...")
        dominio_ip = Dominio.objects.create(
            domain='127.0.0.1',
            tenant=empresa_admin,
            is_primary=True
        )

        print(f"[OK] Dominio registrado: {dominio_ip.domain}\n")

        # Crear dominio localhost
        print("[...] Registrando dominio localhost...")
        dominio_localhost = Dominio.objects.create(
            domain='localhost',
            tenant=empresa_admin,
            is_primary=False
        )

        print(f"[OK] Dominio registrado: {dominio_localhost.domain}\n")

        # Resumen
        print("="*60)
        print("OK - CONFIGURACION COMPLETADA")
        print("="*60 + "\n")

        print("Puedes acceder a:\n")
        print("  - http://127.0.0.1:8000/admin/")
        print("  - http://localhost:8000/admin/\n")

        print("Proximos pasos:\n")
        print("  1. Crea un super usuario:")
        print("     python manage.py createsuperuser\n")
        print("  2. Inicia el servidor:")
        print("     python manage.py runserver\n")
        print("  3. Accede a:")
        print("     http://127.0.0.1:8000/admin/\n")

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("ERROR")
        print("="*60 + "\n")
        print(f"  {str(e)}\n")
        return False


if __name__ == '__main__':
    exito = setup_admin_tenant()
    exit(0 if exito else 1)

