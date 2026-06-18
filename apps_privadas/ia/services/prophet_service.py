import pandas as pd
from prophet import Prophet
from django.utils import timezone
from apps_privadas.venta.models import DetalleVenta
from apps_privadas.ia.services.modelo_store import modelo_vigente, guardar_modelo, cargar_modelo


def _obtener_dataframe():
    detalles = (
        DetalleVenta.objects
        .select_related('venta', 'variante_producto__producto__categoria')
        .filter(venta__estado='completado')
        .values('venta__fecha', 'variante_producto__producto__categoria__nombre', 'cantidad')
    )
    if not detalles:
        return None

    df = pd.DataFrame(list(detalles))
    df.rename(columns={
        'venta__fecha': 'fecha',
        'variante_producto__producto__categoria__nombre': 'categoria',
    }, inplace=True)
    df['fecha'] = pd.to_datetime(df['fecha']).dt.tz_localize(None)
    df['periodo'] = df['fecha'].dt.to_period('M').dt.to_timestamp()
    return df


def entrenar_y_guardar():
    """Entrena Prophet para todas las categorías y guarda en disco."""
    df = _obtener_dataframe()
    if df is None:
        return 0

    modelos = {}
    for categoria, grupo in df.groupby('categoria'):
        serie = grupo.groupby('periodo')['cantidad'].sum().reset_index()
        serie.columns = ['ds', 'y']
        serie = serie.sort_values('ds')
        if len(serie) < 2:
            continue
        modelo = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        modelo.fit(serie)
        modelos[categoria] = {'modelo': modelo, 'ultimo_historico': serie['ds'].max()}

    guardar_modelo('prophet', modelos, len(df))
    return len(df)


def predecir_por_categoria(fecha_hasta=None, meses_historico=12, forzar=False):
    """
    Modelo 1 — Prophet por categoría.
    Entrena con todoo el historial pero solo devuelve los últimos
    `meses_historico` meses al frontend para mantener el gráfico legible.

    fecha_hasta:     fecha límite de la proyección (YYYY-MM-DD).
                     Sin este param proyecta 3 meses desde hoy.
    meses_historico: cuántos meses recientes mostrar en el gráfico (default: 12).
    forzar:          True para reentrenar ignorando el caché.
    """
    hoy = timezone.now().replace(tzinfo=None)

    if fecha_hasta:
        fecha_hasta_dt = pd.to_datetime(fecha_hasta)
        meses_diff = (fecha_hasta_dt.year - hoy.year) * 12 + (fecha_hasta_dt.month - hoy.month)
        periodos = max(1, meses_diff)
    else:
        periodos = 3

    if forzar or not modelo_vigente('prophet'):
        entrenar_y_guardar()

    modelos = cargar_modelo('prophet')
    if not modelos:
        return {'historico': [], 'proyeccion': [], 'fecha_hasta': str(fecha_hasta or ''), 'meses_historico': meses_historico}

    resultado = {'historico': [], 'proyeccion': [], 'fecha_hasta': str(fecha_hasta or ''), 'meses_historico': meses_historico}

    # Inicio del mes actual: los meses anteriores son histórico, desde aquí es proyección
    current_period = pd.Timestamp(hoy).to_period('M').to_timestamp()
    # N meses completos anteriores al mes actual
    corte_historico = current_period - pd.DateOffset(months=meses_historico)

    for categoria, datos in modelos.items():
        modelo = datos['modelo']

        futuro = modelo.make_future_dataframe(periods=periodos, freq='MS')
        forecast = modelo.predict(futuro)

        for _, fila in forecast.iterrows():
            entry = {
                'categoria': categoria,
                'periodo': fila['ds'].strftime('%Y-%m'),
                'unidades': round(max(0, fila['yhat'])),
            }
            if fila['ds'] < current_period:
                if fila['ds'] >= corte_historico:
                    resultado['historico'].append(entry)
            else:
                resultado['proyeccion'].append(entry)

    return resultado
