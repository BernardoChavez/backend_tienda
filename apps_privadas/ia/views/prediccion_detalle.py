from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps_privadas.ia.services.rf_service import predecir_por_variante
from apps_privadas.ia.services.alertas_service import crear_alertas_demanda_alta


class PrediccionDetalleView(APIView):
    """
    GET /api/ia/prediccion-detalle/
    Devuelve predicción de demanda por variante con producto y categoría (Random Forest).

    Query params:
      fecha_hasta  — hasta qué fecha proyectar la demanda (YYYY-MM-DD).
                     Sin este param proyecta 30 días desde hoy.
      solo_alerta  — 'true' para mostrar solo variantes con déficit (default: false)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_hasta = request.query_params.get('fecha_hasta')
        solo_alerta = request.query_params.get('solo_alerta', 'false').lower() == 'true'

        predicciones = predecir_por_variante(fecha_hasta=fecha_hasta)

        crear_alertas_demanda_alta(predicciones)

        if solo_alerta:
            predicciones = [p for p in predicciones if p['alerta']]

        return Response({
            'dias_proyectados': dias,
            'total': len(predicciones),
            'predicciones': predicciones,
        })
