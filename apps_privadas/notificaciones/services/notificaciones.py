import json

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps_privadas.notificaciones.models import Notificacion, Promocion
from apps_privadas.seguridad.services.auditoria import registrar_bitacora


class NotificacionService:
    @staticmethod
    def suscribir_usuario(usuario, endpoint, p256dh, auth, user_agent=''):
        notificacion, _ = Notificacion.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'usuario': usuario,
                'p256dh': p256dh,
                'auth': auth,
                'user_agent': user_agent or '',
                'activa': True,
                'ultimo_error': '',
            }
        )
        return notificacion

    @staticmethod
    def desuscribir_usuario(usuario, endpoint=None):
        queryset = Notificacion.objects.filter(usuario=usuario, activa=True)
        if endpoint:
            queryset = queryset.filter(endpoint=endpoint)
        return queryset.update(activa=False)

    @staticmethod
    @transaction.atomic
    def publicar_promocion(promocion, usuario, request=None):
        if promocion.estado == Promocion.ESTADO_PUBLICADA:
            return {
                'success': False,
                'error': 'La promocion ya esta publicada.',
            }

        promocion.estado = Promocion.ESTADO_PUBLICADA
        promocion.fecha_publicacion = timezone.now()
        promocion.save(update_fields=['estado', 'fecha_publicacion', 'fecha_actualizacion'])

        suscripciones = Notificacion.objects.select_for_update().filter(activa=True)
        enviadas = 0
        fallidas = 0

        for notificacion in suscripciones:
            ok, error = NotificacionService._enviar_push(notificacion, promocion)
            notificacion.ultima_promocion = promocion
            notificacion.ultimo_envio = timezone.now()
            notificacion.ultimo_error = error or ''

            if ok:
                enviadas += 1
            else:
                fallidas += 1
                if NotificacionService._debe_desactivar(error):
                    notificacion.activa = False

            notificacion.save(update_fields=[
                'ultima_promocion',
                'ultimo_envio',
                'ultimo_error',
                'activa',
                'fecha_actualizacion',
            ])

        registrar_bitacora(
            usuario_id=getattr(usuario, 'id', 0),
            entidad='notificaciones.promocion',
            accion='PUBLICAR_PROMOCION',
            detalles=(
                f"Promocion {promocion.id} publicada. "
                f"Enviadas: {enviadas}. Fallidas: {fallidas}."
            ),
            metodo=getattr(request, 'method', 'POST') if request else 'POST',
            ruta=getattr(request, 'path', f'/api/promociones/{promocion.id}/publicar/') if request else None,
            ip_cliente=NotificacionService._get_client_ip(request) if request else None,
            estado_http=200,
        )

        return {
            'success': True,
            'promocion_id': promocion.id,
            'estado': promocion.estado,
            'notificaciones_activas': suscripciones.count(),
            'enviadas': enviadas,
            'fallidas': fallidas,
            'mensaje': 'Promocion publicada.',
        }

    @staticmethod
    def _enviar_push(notificacion, promocion):
        vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
        vapid_admin_email = getattr(settings, 'VAPID_ADMIN_EMAIL', '')

        if not vapid_private_key or not vapid_admin_email:
            return False, 'VAPID no configurado. Suscripcion guardada, envio real pendiente.'

        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            return False, 'pywebpush no esta instalado.'

        payload = {
            'title': f"Nueva oferta: {promocion.titulo}",
            'body': promocion.descripcion or f"Oferta disponible en {promocion.producto.nombre}",
            'url': f"/promociones/{promocion.id}",
            'promocion_id': promocion.id,
            'producto_id': promocion.producto_id,
        }

        subscription_info = {
            'endpoint': notificacion.endpoint,
            'keys': {
                'p256dh': notificacion.p256dh,
                'auth': notificacion.auth,
            }
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims={'sub': f"mailto:{vapid_admin_email}"},
            )
            return True, ''
        except WebPushException as exc:
            return False, str(exc)
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def _debe_desactivar(error):
        if not error:
            return False
        error = error.lower()
        return '410' in error or '404' in error or 'expired' in error or 'gone' in error

    @staticmethod
    def _get_client_ip(request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

