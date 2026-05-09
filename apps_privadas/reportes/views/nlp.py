import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.nlp import ReporteNLPSerializer
from ..services.llm import LLMTraductorReportes
from ..services.motor_orm import MotorReportesDinamicos

class ReporteNLPView(APIView):
    """Traduce voz/texto a JSON y luego ejecuta la consulta."""

    def post(self, request):
        # 1. Validar que llegó el texto
        serializer = ReporteNLPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        texto_usuario = serializer.validated_data['texto']

        try:
            # 2. Paso A: IA traduce texto -> JSON
            # Nota: La API Key debería venir de tus variables de entorno
            traductor = LLMTraductorReportes(api_key=os.getenv("GEMINI_API_KEY"))
            query_json = traductor.traducir_texto_a_json(texto_usuario)

            # 3. Paso B: El Motor ejecuta el JSON generado
            motor = MotorReportesDinamicos()
            resultado = motor.procesar_reporte(query_json)

            # 4. Devolvemos los datos + la interpretación de la IA (transparencia)
            return Response({
                "query_interpretada": query_json,
                "resultados": resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "La IA no pudo procesar la solicitud o el motor falló",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)