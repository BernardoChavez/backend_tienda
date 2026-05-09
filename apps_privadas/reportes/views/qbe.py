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
            print(f"[DEBUG QBE] validated_data: {serializer.validated_data}")
            resultado = motor.procesar_reporte(serializer.validated_data)
            print(f"[DEBUG QBE] resultado keys: {resultado.keys() if isinstance(resultado, dict) else type(resultado)}")
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValueError as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": "Error interno", "detail": str(e)}, status=500)