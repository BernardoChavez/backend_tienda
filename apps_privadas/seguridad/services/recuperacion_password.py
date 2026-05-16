import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps_privadas.seguridad.models.codigo_recuperacion import CodigoRecuperacion
from apps_privadas.seguridad.models.usuario import Usuario


class RecuperacionPasswordService:
    """Servicio para recuperacion de contrasena via email con codigo aleatorio"""

    EXPIRACION_MINUTOS = 15
    LONGITUD_CODIGO = 8

    @staticmethod
    def _generar_codigo():
        """Genera un codigo alfanumerico aleatorio en mayusculas"""
        caracteres = string.ascii_uppercase + string.digits
        return ''.join(random.choices(caracteres, k=RecuperacionPasswordService.LONGITUD_CODIGO))

    @staticmethod
    def solicitar_recuperacion(username):
        """
        Paso 1: Recibe el username, busca su email y envia el codigo.

        Returns:
            dict: {'success': bool, 'mensaje': str, 'error': str}
        """
        try:
            try:
                usuario = Usuario.objects.get(username=username, is_active=True)
            except Usuario.DoesNotExist:
                return {
                    'success': False,
                    'error': 'No existe un usuario activo con ese nombre de usuario'
                }

            if not usuario.email:
                return {
                    'success': False,
                    'error': 'El usuario no tiene un correo registrado'
                }

            # Invalidar codigos anteriores pendientes
            CodigoRecuperacion.objects.filter(
                usuario=usuario,
                usado=False
            ).update(usado=True)

            # Generar nuevo codigo
            codigo = RecuperacionPasswordService._generar_codigo()
            expira_en = timezone.now() + timedelta(
                minutes=RecuperacionPasswordService.EXPIRACION_MINUTOS
            )

            CodigoRecuperacion.objects.create(
                usuario=usuario,
                codigo=codigo,
                expira_en=expira_en
            )

            # Enviar correo
            send_mail(
                subject='Codigo de recuperacion de contrasena',
                message=(
                    f'Hola {usuario.nombre or usuario.username},\n\n'
                    f'Tu codigo de recuperacion es:\n\n'
                    f'  {codigo}\n\n'
                    f'Este codigo expira en {RecuperacionPasswordService.EXPIRACION_MINUTOS} minutos.\n'
                    f'Si no solicitaste este codigo, ignora este mensaje.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            print(f"✓ Codigo de recuperacion enviado a {usuario.email}")

            # Ocultar parte del email por seguridad (ej: hr****@gmail.com)
            email = usuario.email
            partes = email.split('@')
            email_oculto = partes[0][:2] + '****@' + partes[1]

            return {
                'success': True,
                'mensaje': f'Se envio un codigo de recuperacion a {email_oculto}'
            }

        except Exception as e:
            print(f"❌ Error enviando codigo de recuperacion: {str(e)}")
            return {
                'success': False,
                'error': f'Error al enviar el correo: {str(e)}'
            }

    @staticmethod
    def verificar_codigo(username, codigo):
        """
        Paso 2: Verifica que el codigo ingresado sea valido y no haya expirado.

        Returns:
            dict: {'success': bool, 'mensaje': str, 'error': str}
        """
        try:
            try:
                usuario = Usuario.objects.get(username=username, is_active=True)
            except Usuario.DoesNotExist:
                return {
                    'success': False,
                    'error': 'No existe un usuario activo con ese nombre de usuario'
                }

            registro = CodigoRecuperacion.objects.filter(
                usuario=usuario,
                codigo=codigo.upper(),
                usado=False
            ).order_by('-creado_en').first()

            if not registro:
                return {
                    'success': False,
                    'error': 'Codigo invalido o ya utilizado'
                }

            if not registro.esta_vigente():
                return {
                    'success': False,
                    'error': 'El codigo ha expirado, solicita uno nuevo'
                }

            return {
                'success': True,
                'mensaje': 'Codigo verificado correctamente'
            }

        except Exception as e:
            print(f"❌ Error verificando codigo: {str(e)}")
            return {
                'success': False,
                'error': f'Error al verificar el codigo: {str(e)}'
            }

    @staticmethod
    def cambiar_password(username, codigo, nueva_password):
        """
        Paso 3: Verifica el codigo y actualiza la contrasena del usuario.

        Returns:
            dict: {'success': bool, 'mensaje': str, 'error': str}
        """
        try:
            try:
                usuario = Usuario.objects.get(username=username, is_active=True)
            except Usuario.DoesNotExist:
                return {
                    'success': False,
                    'error': 'No existe un usuario activo con ese nombre de usuario'
                }

            registro = CodigoRecuperacion.objects.filter(
                usuario=usuario,
                codigo=codigo.upper(),
                usado=False
            ).order_by('-creado_en').first()

            if not registro:
                return {
                    'success': False,
                    'error': 'Codigo invalido o ya utilizado'
                }

            if not registro.esta_vigente():
                return {
                    'success': False,
                    'error': 'El codigo ha expirado, solicita uno nuevo'
                }

            # Cambiar contrasena
            usuario.set_password(nueva_password)
            usuario.save()

            # Marcar codigo como usado
            registro.usado = True
            registro.save()

            print(f"✓ Contrasena cambiada para {usuario.username}")

            return {
                'success': True,
                'mensaje': 'Contrasena actualizada correctamente'
            }

        except Exception as e:
            print(f"❌ Error cambiando contrasena: {str(e)}")
            return {
                'success': False,
                'error': f'Error al cambiar la contrasena: {str(e)}'
            }

