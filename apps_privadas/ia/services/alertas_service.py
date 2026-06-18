from apps_privadas.ia.models import AlertaReabastecimiento
from apps_privadas.inventario.models import VarianteProducto


def verificar_stock_post_venta(variante):
    """
    Tipo A: Se llama después de cada venta.
    Crea alerta si el stock actual cayó al límite mínimo o por debajo.
    No duplica si ya existe una alerta no leída para esa variante.
    """
    if variante.cantidad > variante.limite_cantidad:
        return

    ya_existe = AlertaReabastecimiento.objects.filter(
        variante=variante,
        tipo='stock_bajo',
        leida=False,
    ).exists()

    if not ya_existe:
        AlertaReabastecimiento.objects.create(
            tipo='stock_bajo',
            variante=variante,
            stock_actual=variante.cantidad,
            limite_minimo=variante.limite_cantidad,
        )


def crear_alertas_demanda_alta(predicciones):
    """
    Tipo B: Se llama al ejecutar el modelo Random Forest.
    Crea alertas para variantes donde la demanda proyectada supera el stock.
    No duplica si ya existe una alerta no leída del mismo tipo para esa variante.
    """
    ids_con_alerta = [p['variante_id'] for p in predicciones if p['alerta']]
    if not ids_con_alerta:
        return

    variantes = {v.id: v for v in VarianteProducto.objects.filter(id__in=ids_con_alerta)}
    existentes = set(
        AlertaReabastecimiento.objects.filter(
            variante_id__in=ids_con_alerta,
            tipo='demanda_alta',
            leida=False,
        ).values_list('variante_id', flat=True)
    )

    nuevas = []
    for pred in predicciones:
        if not pred['alerta']:
            continue
        vid = pred['variante_id']
        if vid in existentes:
            continue
        variante = variantes.get(vid)
        if not variante:
            continue
        nuevas.append(AlertaReabastecimiento(
            tipo='demanda_alta',
            variante=variante,
            stock_actual=pred['stock_actual'],
            limite_minimo=pred['limite_minimo'],
            demanda_proyectada=pred['demanda_proyectada'],
            dias_proyectados=pred['dias_proyectados'],
        ))

    if nuevas:
        AlertaReabastecimiento.objects.bulk_create(nuevas)
