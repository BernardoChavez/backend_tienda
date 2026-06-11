from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class AutomaticBackupSimulatedView(APIView):
    """
    Simula la creacion de un backup automatico para el tenant actual.

    Endpoint: POST /api/seguridad/backup/automatico/
    Body (JSON, opcional):
    {
        "hora": "02:00",
        "tipo": "full"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        hora = request.data.get('hora') or '02:00'
        tipo = request.data.get('tipo') or 'full'
        tenant = request.tenant.schema_name
        ahora = timezone.now()

        payload = {
            'success': True,
            'tenant': tenant,
            'hora_programada': hora,
            'tipo': tipo,
            'estado': 'simulado',
            'ruta_guardado': f'media/backups/{tenant}/backup_{ahora:%Y%m%d_%H%M%S}.dump',
            'creado_en': ahora.isoformat(),
            'mensaje': 'Backup automatico simulado creado'
        }

        return Response(payload, status=status.HTTP_201_CREATED)

