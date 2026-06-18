import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from django.utils import timezone
from apps_privadas.venta.models import DetalleVenta
from apps_privadas.ia.services.modelo_store import modelo_vigente, guardar_modelo, cargar_modelo


def _obtener_dataframe():
    detalles = (
        DetalleVenta.objects
        .select_related('venta', 'variante__producto__categoria')
        .filter(venta__estado='completado')
        .values(
            'venta__fecha',
            'variante__id',
            'variante__sku',
            'variante__precio',
            'variante__cantidad',
            'variante__limite_cantidad',
            'variante__producto__nombre',
            'variante__producto__categoria__nombre',
            'variante__producto__categoria__id',
            'cantidad',
        )
    )
    if not detalles:
        return None

    df = pd.DataFrame(list(detalles))
    df.rename(columns={
        'venta__fecha': 'fecha',
        'variante__id': 'variante_id',
        'variante__sku': 'sku',
        'variante__precio': 'precio',
        'variante__cantidad': 'stock_actual',
        'variante__limite_cantidad': 'limite_minimo',
        'variante__producto__nombre': 'producto',
        'variante__producto__categoria__nombre': 'categoria',
        'variante__producto__categoria__id': 'categoria_id',
        'cantidad': 'unidades',
    }, inplace=True)
    df['fecha'] = pd.to_datetime(df['fecha']).dt.tz_localize(None)
    df['mes'] = df['fecha'].dt.month
    df['trimestre'] = df['fecha'].dt.quarter
    df['periodo'] = df['fecha'].dt.to_period('M').dt.to_timestamp()
    return df


def entrenar_y_guardar():
    """Entrena Random Forest y guarda modelo + encoder en disco."""
    df = _obtener_dataframe()
    if df is None:
        return 0

    por_periodo = (
        df.groupby(['variante_id', 'periodo', 'sku', 'precio', 'stock_actual',
                    'limite_minimo', 'producto', 'categoria', 'categoria_id'])
        .agg(unidades=('unidades', 'sum'), mes=('mes', 'first'), trimestre=('trimestre', 'first'))
        .reset_index()
        .sort_values(['variante_id', 'periodo'])
    )

    le_categoria = LabelEncoder()
    por_periodo['categoria_enc'] = le_categoria.fit_transform(por_periodo['categoria'])

    features = ['mes', 'trimestre', 'categoria_enc', 'precio']
    datos_entrenamiento = por_periodo.dropna(subset=features + ['unidades'])

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(datos_entrenamiento[features], datos_entrenamiento['unidades'])

    guardar_modelo('random_forest', {'modelo': modelo, 'encoder': le_categoria}, len(df))
    return len(df)


def predecir_por_variante(fecha_hasta=None, forzar=False):
    """
    Modelo 2 — Random Forest por variante.
    Carga el modelo desde disco si está vigente; si no, entrena primero.

    fecha_hasta: fecha límite de la proyección (YYYY-MM-DD).
                 Sin este param proyecta 30 días desde hoy.
    forzar:      True para reentrenar ignorando el caché.
    """
    hoy = timezone.now().date()

    if fecha_hasta:
        fecha_hasta_dt = pd.to_datetime(fecha_hasta).date()
        dias = max(1, (fecha_hasta_dt - hoy).days)
        mes_pred = pd.to_datetime(fecha_hasta).month
    else:
        dias = 30
        mes_pred = (hoy.month % 12) + 1

    trimestre_pred = ((mes_pred - 1) // 3) + 1

    if forzar or not modelo_vigente('random_forest'):
        entrenar_y_guardar()

    cache = cargar_modelo('random_forest')
    if not cache:
        return []

    modelo = cache['modelo']
    le_categoria = cache['encoder']

    df = _obtener_dataframe()
    if df is None:
        return []

    por_periodo = (
        df.groupby(['variante_id', 'periodo', 'sku', 'precio', 'stock_actual',
                    'limite_minimo', 'producto', 'categoria', 'categoria_id'])
        .agg(unidades=('unidades', 'sum'), mes=('mes', 'first'), trimestre=('trimestre', 'first'))
        .reset_index()
        .sort_values(['variante_id', 'periodo'])
    )

    categorias_conocidas = set(le_categoria.classes_)
    resultado = []

    for _, grupo in por_periodo.groupby('variante_id'):
        ultima_fila = grupo.iloc[-1]
        categoria = ultima_fila['categoria']

        if categoria not in categorias_conocidas:
            continue

        categoria_enc = le_categoria.transform([categoria])[0]

        X_pred = pd.DataFrame([{
            'mes': mes_pred,
            'trimestre': trimestre_pred,
            'categoria_enc': categoria_enc,
            'precio': float(ultima_fila['precio']),
        }])

        unidades_proj = max(0, round(modelo.predict(X_pred)[0]))
        stock = int(ultima_fila['stock_actual'])
        limite = int(ultima_fila['limite_minimo'])
        deficit = max(0, unidades_proj - stock)

        resultado.append({
            'variante_id': int(ultima_fila['variante_id']),
            'variante_sku': ultima_fila['sku'],
            'producto': ultima_fila['producto'],
            'categoria': categoria,
            'stock_actual': stock,
            'limite_minimo': limite,
            'demanda_proyectada': unidades_proj,
            'dias_proyectados': dias,
            'deficit': deficit,
            'alerta': unidades_proj > stock,
        })

    resultado.sort(key=lambda x: x['deficit'], reverse=True)
    return resultado
