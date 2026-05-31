from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.voz import ReporteVozSerializer
from ..services.stt_client import transcribir_audio


class ReporteVozView(APIView):
    """Transcribe audio a texto usando el servicio STT."""

    def post(self, request):
        serializer = ReporteVozSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_file = serializer.validated_data["audio"]
        try:
            texto = transcribir_audio(
                audio_bytes=audio_file.read(),
                filename=audio_file.name,
            )
            return Response({"texto_transcrito": texto}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": "Error al transcribir audio", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
