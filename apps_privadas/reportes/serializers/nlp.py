from rest_framework import serializers

class ReporteNLPSerializer(serializers.Serializer):
    """
    Valida la entrada de lenguaje natural. 
    Aquí no validamos filtros porque eso lo inventará la IA.
    """
    texto = serializers.CharField(
        required=True, 
        min_length=3,
        help_text="El comando de voz o texto enviado por el usuario."
    )
    
    # Opcional: podrías pasar un contexto de idioma o zona horaria aquí
    idioma = serializers.CharField(default="es", required=False)