#!/usr/bin/env python
"""
Script para crear o actualizar un superusuario en el tenant tienda_amiga.

Uso:
    python create_tenant_superuser.py
    python create_tenant_superuser.py admin admin@tienda-amiga.com tienda2024
"""

import os
import sys
from getpass import getpass

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tienda.settings')
django.setup()

from django_tenants.utils import schema_context

from apps_privadas.seguridad.models.usuario import Usuario

SCHEMA = 'tienda_amiga'


def crear_superuser():
    print("\n" + "=" * 60)
    print("CREAR O ACTUALIZAR SUPERUSUARIO - TIENDA AMIGA")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        username = sys.argv[1]
        email = sys.argv[2] if len(sys.argv) > 2 else None
        password = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass("Password (min 8 caracteres): ")
        password_confirm = getpass("Confirmar password: ")

        if password != password_confirm:
            print("\n[ERROR] Las contrasenas no coinciden\n")
            return False

    if not username:
        print("\n[ERROR] Username es requerido\n")
        return False

    if not email or '@' not in email:
        print("\n[ERROR] Email valido es requerido\n")
        return False

    if not password or len(password) < 8:
        print("\n[ERROR] La password debe tener al menos 8 caracteres\n")
        return False

    try:
        with schema_context(SCHEMA):
            usuario = Usuario.objects.filter(username=username).first()

            if usuario:
                usuario.email = email
                usuario.is_staff = True
                usuario.is_superuser = True
                usuario.is_active = True
                usuario.set_password(password)
                usuario.save()
                accion = "actualizado"
            else:
                Usuario.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
                accion = "creado"

            print("\n" + "=" * 60)
            print(f"SUPERUSUARIO {accion.upper()} EXITOSAMENTE")
            print("=" * 60 + "\n")
            print("  Tenant: Tienda Amiga")
            print(f"  Username: {username}")
            print(f"  Email: {email}\n")
            print("Login API:")
            print("  POST http://tienda-amiga.localhost:8000/api/login/")
            print("Admin:")
            print("  http://tienda-amiga.localhost:8000/admin/\n")

            return True

    except Exception as exc:
        print(f"\n[ERROR] {exc}\n")
        return False


if __name__ == '__main__':
    raise SystemExit(0 if crear_superuser() else 1)
