from rest_framework import serializers


class ReporteVozSerializer(serializers.Serializer):
    audio = serializers.FileField(
        help_text="Archivo de audio (wav, mp3, etc.) para transcribir"
    )
