import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.nlp import ReporteNLPSerializer
from ..services.llm import LLMTraductorReportes
from ..services.motor_orm import MotorReportesDinamicos


class ReporteNLPView(APIView):
    """Traduce voz/texto a JSON y luego ejecuta la consulta."""

    def post(self, request):
        serializer = ReporteNLPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        texto_usuario = serializer.validated_data['texto']
        print(f"[DEBUG NLP] texto recibido: {texto_usuario}")

        api_key = os.getenv("OPENROUTER_API_KEY")
        print(f"[DEBUG NLP] api_key presente: {bool(api_key)}")

        if not api_key:
            return Response({
                "error": "API key no configurada",
                "detail": "Configura OPENROUTER_API_KEY en el .env del backend"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            traductor = LLMTraductorReportes(api_key=api_key)
            print("[DEBUG NLP] llamando a la IA...")
            start = time.time()
            query_json = traductor.traducir_texto_a_json(texto_usuario)
            elapsed = time.time() - start
            print(f"[TIMING NLP] traducción completada en {elapsed:.2f}s")
            print(f"[DEBUG NLP] IA respondió: {query_json}")

            motor = MotorReportesDinamicos()
            print("[DEBUG NLP] ejecutando motor...")
            resultado = motor.procesar_reporte(query_json)
            print(f"[DEBUG NLP] motor OK, {len(resultado.get('datos', []))} registros")

            return Response({
                "query_interpretada": query_json,
                "resultados": resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "error": "La IA no pudo procesar la solicitud o el motor falló",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            traductor = LLMTraductorReportes(api_key=api_key)
            print("[DEBUG NLP] llamando a la IA...")
            query_json = traductor.traducir_texto_a_json(texto_usuario)
            print(f"[DEBUG NLP] IA respondió: {query_json}")

            motor = MotorReportesDinamicos()
            print("[DEBUG NLP] ejecutando motor...")
            resultado = motor.procesar_reporte(query_json)
            print(f"[DEBUG NLP] motor OK, {len(resultado.get('datos', []))} registros")

            return Response({
                "query_interpretada": query_json,
                "resultados": resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "error": "La IA no pudo procesar la solicitud o el motor falló",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)