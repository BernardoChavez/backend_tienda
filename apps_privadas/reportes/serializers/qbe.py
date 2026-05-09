from .reporte_base import ReporteBaseSerializer
from rest_framework import serializers
from ..config_reportes import REPORT_CONFIG


class ReporteQBESerializer(ReporteBaseSerializer):
    vista_logica = serializers.ChoiceField(
        choices=list(REPORT_CONFIG["modelos"].keys())
    )
    filtros = ReporteBaseSerializer.FiltroSerializer(many=True, required=False)
    agrupar_por = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    metricas_agrupadas = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    filtros_having = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    ventana = serializers.DictField(required=False)

    def validate_vista_logica(self, value):
        if value not in REPORT_CONFIG["mapa_campos"]:
            raise serializers.ValidationError(
                f"Vista logica '{value}' no tiene configuracion de campos"
            )
        return value