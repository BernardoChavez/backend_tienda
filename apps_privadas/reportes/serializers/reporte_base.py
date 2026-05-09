from rest_framework import serializers


class ReporteBaseSerializer(serializers.Serializer):
    class FiltroSerializer(serializers.Serializer):
        campo = serializers.CharField()
        operador = serializers.CharField(default="exact")
        valor = serializers.JSONField()

    class PaginacionSerializer(serializers.Serializer):
        pagina = serializers.IntegerField(default=1, min_value=1)
        cantidad_por_pagina = serializers.IntegerField(default=50, min_value=1, max_value=200)

    ordenar_por = serializers.CharField(required=False, allow_blank=True)
    paginacion = PaginacionSerializer(required=False)