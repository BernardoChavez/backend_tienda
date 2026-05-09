from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.qbe import ReporteQBESerializer
from ..services.motor_orm import MotorReportesDinamicos

class ReporteQBEView(APIView):
    """Maneja consultas directas desde el formulario de filtros (QBE)."""

    def post(self, request):
        # 1. Validar con el serializer específico de QBE
        serializer = ReporteQBESerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Estructura de consulta inválida",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Procesar con el motor
        try:
            motor = MotorReportesDinamicos()
            # Usamos validated_data para asegurar tipos de datos correctos
            resultado = motor.procesar_reporte(serializer.validated_data)
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Error interno", "detail": str(e)}, status=500)