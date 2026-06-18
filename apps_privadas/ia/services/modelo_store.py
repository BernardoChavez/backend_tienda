import os
import joblib
from datetime import timedelta
from django.conf import settings
from django.db import connection
from django.utils import timezone


def get_tenant_model_dir():
    schema = connection.schema_name
    path = os.path.join(settings.BASE_DIR, 'media', 'modelos_ia', schema)
    os.makedirs(path, exist_ok=True)
    return path


def modelo_vigente(tipo):
    from apps_privadas.ia.models import ModeloEntrenado
    horas = getattr(settings, 'IA_MODELO_HORAS_VIGENCIA', 24)
    limite = timezone.now() - timedelta(hours=horas)
    return ModeloEntrenado.objects.filter(
        tipo=tipo,
        vigente=True,
        fecha_entrenamiento__gte=limite,
    ).exists()


def guardar_modelo(tipo, objeto, total_registros):
    from apps_privadas.ia.models import ModeloEntrenado
    ruta = os.path.join(get_tenant_model_dir(), f'{tipo}.pkl')
    joblib.dump(objeto, ruta)
    ModeloEntrenado.objects.filter(tipo=tipo).update(vigente=False)
    ModeloEntrenado.objects.create(
        tipo=tipo,
        ruta_archivo=ruta,
        total_registros=total_registros,
        vigente=True,
    )


def cargar_modelo(tipo):
    from apps_privadas.ia.models import ModeloEntrenado
    registro = ModeloEntrenado.objects.filter(tipo=tipo, vigente=True).first()
    if registro and os.path.exists(registro.ruta_archivo):
        return joblib.load(registro.ruta_archivo)
    return None
