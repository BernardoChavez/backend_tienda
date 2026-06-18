from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps_privadas.ia.services.prophet_service import predecir_por_categoria


class DashboardVentasView(APIView):
    """
    GET /api/ia/dashboard/
    Devuelve ventas históricas reales + proyección por categoría (Prophet).

    Query params:
      fecha_hasta — hasta qué fecha mostrar la proyección (YYYY-MM-DD).
                    Sin este param proyecta 3 meses desde hoy.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_hasta = request.query_params.get('fecha_hasta')
        data = predecir_por_categoria(fecha_hasta=fecha_hasta)
        return Response(data)