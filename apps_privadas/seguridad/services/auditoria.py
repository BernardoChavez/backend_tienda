from django.utils import timezone

from apps_privadas.seguridad.models.bitacora_auditoria import BitacoraAuditoria


def registrar_bitacora(
    *,
    usuario_id,
    entidad,
    accion,
    detalles='',
    metodo=None,
    ruta=None,
    ip_cliente=None,
    estado_http=None,
):
    """Registra un evento de auditoria sin interrumpir el flujo principal."""
    ahora = timezone.localtime()
    detalles = str(detalles or '')[:500]
    entidad = str(entidad or 'sistema')[:100]
    accion = str(accion or 'ACCION')[:100]

    try:
        return BitacoraAuditoria.objects.create(
            fecha=ahora.date(),
            hora=ahora.time(),
            entidad=entidad,
            detalles=detalles,
            accion=accion,
            usuarios_id=usuario_id or 0,
            metodo=(metodo or '')[:10] or None,
            ruta=(ruta or '')[:255] or None,
            ip_cliente=ip_cliente,
            estado_http=estado_http,
        )
    except Exception as exc:
        print(f"[AUDITORIA] No se pudo registrar bitacora: {exc}")
        return None

