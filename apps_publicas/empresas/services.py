from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from apps_publicas.empresas.models import Empresa, Dominio, Plan, Suscripcion, SuscripcionCambio, EstadoSuscripcion, CicloSuscripcion
from apps_privadas.seguridad.models import Usuario
import re
import os
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.message,
                self.from_email,
                self.recipient_list,
                fail_silently=True, # Es vital que sea True para que no rompa el hilo si falla
            )
        except Exception as e:
            print(f"Error en el hilo de correo: {e}")


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
    def crear_empresa_con_admin(nombre_empresa, correo_empresa, super_admin_data, plan, ciclo):
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

            # 3. Crear suscripcion inicial en el esquema public
            SuscripcionService.crear_suscripcion({
                'empresa': empresa,
                'plan': plan,
                'ciclo': ciclo,
                'estado': EstadoSuscripcion.ACTIVA,
            })

            # 4. Crear super admin en el esquema de la empresa
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

            # 5. Enviar correo al super admin
            try:
                subject = f"Bienvenido {nombre_empresa}"
                message = (
                    f"Hola {super_admin.username},\n\n"
                    f"Tu empresa '{nombre_empresa}' fue creada exitosamente.\n"
                    f"Acceso: http://{dominio.domain}/login/\n"
                    f"Usuario: {super_admin.username}\n\n"
                    "Si no solicitaste este registro, ignora este mensaje."
                )
                # send_mail(
                #     subject,
                #     message,
                #     settings.DEFAULT_FROM_EMAIL,
                #     [email],
                #     fail_silently=False,
                # )
                EmailThread(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                ).start()
            except Exception as exc:
                print(f"⚠️ No se pudo enviar el correo: {str(exc)}")

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


class PlanService:
    @staticmethod
    def listar_planes(activos_only=False):
        queryset = Plan.objects.all()
        if activos_only:
            queryset = queryset.filter(activo=True)
        return queryset

    @staticmethod
    def crear_plan(data):
        return Plan.objects.create(**data)

    @staticmethod
    def actualizar_plan(instancia, data):
        for campo, valor in data.items():
            setattr(instancia, campo, valor)
        instancia.save()
        return instancia

    @staticmethod
    def eliminar_plan(instancia):
        instancia.delete()


class SuscripcionService:
    @staticmethod
    @transaction.atomic
    def crear_suscripcion(data):
        empresa = data.get('empresa')
        plan = data.get('plan')

        if not plan.activo:
            raise ValueError('El plan seleccionado no está activo.')

        if Suscripcion.objects.filter(empresa=empresa, estado=EstadoSuscripcion.ACTIVA).exists():
            raise ValueError('La empresa ya tiene una suscripcion activa.')

        return Suscripcion.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def actualizar_suscripcion(instancia, data):
        plan_anterior = instancia.plan
        plan_nuevo = data.get('plan', instancia.plan)

        for campo, valor in data.items():
            setattr(instancia, campo, valor)
        instancia.save()

        if plan_anterior != plan_nuevo:
            SuscripcionCambio.objects.create(
                suscripcion=instancia,
                plan_anterior=plan_anterior,
                plan_nuevo=plan_nuevo,
                motivo=data.get('motivo', '')
            )

        return instancia

    @staticmethod
    @transaction.atomic
    def cancelar_suscripcion(instancia, cancelada_por='', motivo=''):
        instancia.estado = EstadoSuscripcion.CANCELADA
        instancia.cancelada_en = timezone.now()
        instancia.cancelada_por = cancelada_por or instancia.cancelada_por
        instancia.auto_renovar = False
        instancia.save()

        if motivo:
            SuscripcionCambio.objects.create(
                suscripcion=instancia,
                plan_anterior=instancia.plan,
                plan_nuevo=instancia.plan,
                motivo=motivo
            )

        return instancia

    @staticmethod
    @transaction.atomic
    def renovar_suscripcion(instancia, renovada_por='', motivo=''):
        ahora = timezone.now()
        if instancia.ciclo == CicloSuscripcion.ANUAL:
            nueva_fecha_fin = ahora + timedelta(days=365)
        else:
            nueva_fecha_fin = ahora + timedelta(days=30)

        instancia.estado = EstadoSuscripcion.ACTIVA
        instancia.ultima_renovacion = ahora
        instancia.fecha_fin = nueva_fecha_fin
        instancia.auto_renovar = True
        instancia.save()

        SuscripcionCambio.objects.create(
            suscripcion=instancia,
            plan_anterior=instancia.plan,
            plan_nuevo=instancia.plan,
            motivo=motivo or f"Renovacion por {renovada_por or 'sistema'}"
        )

        return instancia


class SuscripcionCambioService:
    @staticmethod
    def listar_cambios(suscripcion_id=None):
        queryset = SuscripcionCambio.objects.select_related('suscripcion', 'plan_anterior', 'plan_nuevo')
        if suscripcion_id:
            queryset = queryset.filter(suscripcion_id=suscripcion_id)
        return queryset

