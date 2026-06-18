from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps_privadas.ia.services.prophet_service import entrenar_y_guardar as entrenar_prophet
from apps_privadas.ia.services.rf_service import entrenar_y_guardar as entrenar_rf


class ReentrenarView(APIView):
    """
    POST /api/ia/reentrenar/
    Fuerza el reentrenamiento de ambos modelos para el tenant actual.
    Útil después de cargar datasets masivos o cuando se quiere refrescar
    las predicciones sin esperar las 24h de vigencia.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        registros_rf = entrenar_rf()
        registros_prophet = entrenar_prophet()

        return Response({
            'detalle': 'Modelos reentrenados correctamente.',
            'random_forest': {'registros_usados': registros_rf},
            'prophet': {'registros_usados': registros_prophet},
        })
