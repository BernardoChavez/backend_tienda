#!/usr/bin/env python
"""
Script para crear super usuario en el tenant tienda_amiga.

Uso:
    python create_tenant_superuser.py

O con parámetros:
    python create_tenant_superuser.py admin admin@tienda-amiga.com tienda2024
"""

import os
import sys
import django
from getpass import getpass

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tienda.settings')
django.setup()

from apps_privadas.seguridad.models.usuario import Usuario
from django_tenants.utils import schema_context

SCHEMA = 'tienda_amiga'


def crear_superuser():
    """Crea un super usuario en tienda_amiga"""

    print("\n" + "="*60)
    print("🔐 CREAR SUPER USUARIO - TIENDA AMIGA")
    print("="*60 + "\n")

    # Obtener datos interactivamente o desde argumentos
    if len(sys.argv) > 1:
        username = sys.argv[1]
        email = sys.argv[2] if len(sys.argv) > 2 else None
        password = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass("Password (mín 8 caracteres): ")
        password_confirm = getpass("Confirmar password: ")

        if password != password_confirm:
            print("\n❌ Las contraseñas no coinciden\n")
            return False

    # Validaciones
    if not username:
        print("\n❌ Username es requerido\n")
        return False

    if not email or '@' not in email:
        print("\n❌ Email válido es requerido\n")
        return False

    if not password or len(password) < 8:
        print("\n❌ La password debe tener al menos 8 caracteres\n")
        return False

    try:
        # Cambiar contexto al tenant tienda_amiga
        with schema_context(SCHEMA):
            # Verificar si usuario ya existe
            if Usuario.objects.filter(username=username).exists():
                print(f"\n❌ El usuario '{username}' ya existe\n")
                return False

            # Crear super usuario
            usuario = Usuario.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            print("\n" + "="*60)
            print("✅ SUPER USUARIO CREADO EXITOSAMENTE")
            print("="*60 + "\n")
            print(f"  Tenant: Tienda Amiga")
            print(f"  Username: {username}")
            print(f"  Email: {email}\n")
            print(f"Accede a: http://tienda-amiga.localhost:8000/admin/\n")

            return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        return False


if __name__ == '__main__':
    crear_superuser()
