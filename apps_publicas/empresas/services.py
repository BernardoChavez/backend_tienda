from django.db import transaction
from apps_publicas.empresas.models import Empresa, Dominio
from apps_privadas.seguridad.models import Usuario
import re
import os


class EmpresaRegistroService:
    """
    Servicio para crear una empresa completa con su super admin.

    Maneja:
    - Creación de la empresa
    - Generación del schema_name
    - Generación del dominio
    - Creación del super admin para el tenant
    - Migraciones automáticas
    """

    @staticmethod
    def generate_schema_name(nombre_empresa):
        """
        Genera un schema_name válido a partir del nombre de la empresa.

        Ejemplo:
            "Tienda Amiga" -> "tienda_amiga"
            "Mi Super Negocio" -> "mi_super_negocio"
        """
        # Convertir a minúsculas
        schema = nombre_empresa.lower()
        # Reemplazar espacios con guiones bajos
        schema = schema.replace(' ', '_')
        # Remover caracteres especiales (mantener solo letras, números y guiones bajos)
        schema = re.sub(r'[^a-z0-9_]', '', schema)
        # Remover guiones bajos múltiples
        schema = re.sub(r'_+', '_', schema)
        # Remover guiones bajos al inicio o final
        schema = schema.strip('_')

        return schema

    @staticmethod
    def generate_dominio(nombre_empresa):
        """
        Genera un dominio válido a partir del nombre de la empresa.

        Ejemplo:
            "Tienda Amiga" -> "tienda-amiga.localhost"
            "Mi Super Negocio" -> "mi-super-negocio.localhost"
        """
        # Convertir a minúsculas
        dominio = nombre_empresa.lower()
        # Reemplazar espacios con guiones
        dominio = dominio.replace(' ', '-')
        # Remover caracteres especiales
        dominio = re.sub(r'[^a-z0-9-]', '', dominio)
        # Remover guiones múltiples
        dominio = re.sub(r'-+', '-', dominio)
        # Remover guiones al inicio o final
        dominio = dominio.strip('-')

        dominio_base = os.environ.get('BASE_DOMAIN', 'localhost')

        # En desarrollo usa .localhost, en producción cambiar
        return f"{dominio}.{dominio_base}"

    @staticmethod
    @transaction.atomic
    def crear_empresa_con_admin(nombre_empresa, correo_empresa, super_admin_data):
        """
        Crea una empresa completa con su super admin en una sola transacción.

        Args:
            nombre_empresa (str): Nombre de la empresa
            correo_empresa (str): Correo de la empresa
            super_admin_data (dict): {
                'username': str,
                'email': str,
                'password': str
            }

        Returns:
            dict: {
                'success': bool,
                'empresa_id': int,
                'nombre': str,
                'schema_name': str,
                'dominio': str,
                'super_admin_username': str,
                'mensaje': str
            }

        Raises:
            ValueError: Si hay error en los datos
            Exception: Si algo falla en la creación
        """

        try:
            # Generar schema y dominio
            schema_name = EmpresaRegistroService.generate_schema_name(nombre_empresa)
            dominio_name = EmpresaRegistroService.generate_dominio(nombre_empresa)

            # Verificar que schema_name no exista
            if Empresa.objects.filter(schema_name=schema_name).exists():
                raise ValueError(
                    f"Ya existe una empresa con el schema '{schema_name}'. "
                    f"Intenta con otro nombre."
                )

            # Verificar que el dominio no exista
            if Dominio.objects.filter(domain=dominio_name).exists():
                raise ValueError(
                    f"El dominio '{dominio_name}' ya está registrado. "
                    f"Intenta con otro nombre."
                )

            # 1. Crear la empresa en el esquema public
            empresa = Empresa.objects.create(
                nombre=nombre_empresa,
                schema_name=schema_name,
                correo=correo_empresa,
                is_active=True
            )

            print(f"✓ Empresa creada: {empresa.nombre} (ID: {empresa.id})")
            print(f"  Schema: {empresa.schema_name}")

            # 2. Crear el dominio
            dominio = Dominio.objects.create(
                domain=dominio_name,
                tenant=empresa,
                is_primary=True
            )

            print(f"✓ Dominio creado: {dominio.domain}")

            # 3. Crear super admin en el esquema de la empresa
            from django_tenants.utils import schema_context
            
            # Validar y limpiar datos ANTES
            username = super_admin_data.get('username')
            email = super_admin_data.get('email')
            password = super_admin_data.get('password')
            
            # Validar que no sean None
            if not username or not email or not password:
                raise ValueError("Username, email y password son requeridos")
            
            # Convertir a string y limpiar
            username = str(username).strip()
            email = str(email).strip()
            password = str(password).strip()
            
            print(f"📝 Datos para crear super admin:")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"  Password: {'*' * len(password)}")
            
            # Usar el schema_name en lugar del objeto empresa
            with schema_context(schema_name):
                # Extraer nombre y apellido del email o username
                nombre = username.split('_')[0] if '_' in username else username
                apellido = username.split('_')[1] if '_' in username else 'Admin'
                
                # Crear el super admin usando Usuario (que hereda de AbstractUser)
                super_admin = Usuario.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    nombre=nombre.capitalize(),
                    apellido=apellido.capitalize()
                )

                print(f"✓ Super admin creado: {super_admin.username} en schema {schema_name}")

            # Retornar respuesta exitosa
            return {
                'success': True,
                'empresa_id': empresa.id,
                'nombre': empresa.nombre,
                'schema_name': empresa.schema_name,
                'dominio': dominio.domain,
                'super_admin_username': super_admin.username,
                'mensaje': (
                    f"Empresa '{nombre_empresa}' creada exitosamente. "
                    f"Accede a http://{dominio.domain}:8000/admin/ "
                    f"con usuario '{super_admin.username}'"
                )
            }

        except ValueError as e:
            # Error de validación
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            # Error inesperado
            print(f"❌ Error creando empresa: {str(e)}")
            return {
                'success': False,
                'error': f"Error creando la empresa: {str(e)}"
            }


class EmpresaListaService:
    """Servicio para operaciones de lectura de empresas"""

    @staticmethod
    def obtener_todas_empresas():
        """Obtiene todas las empresas registradas"""
        empresas = Empresa.objects.filter(is_active=True).values(
            'id', 'nombre', 'correo', 'schema_name', 'fecha_creacion'
        )
        return list(empresas)

    @staticmethod
    def obtener_empresa_por_id(empresa_id):
        """Obtiene una empresa específica"""
        try:
            empresa = Empresa.objects.get(id=empresa_id, is_active=True)
            dominio = Dominio.objects.filter(tenant=empresa).first()

            return {
                'id': empresa.id,
                'nombre': empresa.nombre,
                'correo': empresa.correo,
                'schema_name': empresa.schema_name,
                'dominio': dominio.domain if dominio else None,
                'fecha_creacion': empresa.fecha_creacion
            }
        except Empresa.DoesNotExist:
            return None

    @staticmethod
    def obtener_dominio_por_empresa(empresa_id):
        """Obtiene el dominio principal de una empresa"""
        try:
            dominio = Dominio.objects.get(
                tenant_id=empresa_id,
                is_primary=True
            )
            return dominio.domain
        except Dominio.DoesNotExist:
            return None

