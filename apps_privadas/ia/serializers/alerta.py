from rest_framework import serializers
from apps_privadas.ia.models import AlertaReabastecimiento


class AlertaReabastecimientoSerializer(serializers.ModelSerializer):
    variante_sku = serializers.CharField(source='variante.sku', read_only=True)
    producto = serializers.CharField(source='variante.producto.nombre', read_only=True)
    categoria = serializers.CharField(source='variante.producto.categoria.nombre', read_only=True)
    deficit = serializers.SerializerMethodField()

    class Meta:
        model = AlertaReabastecimiento
        fields = [
            'id',
            'tipo',
            'variante_sku',
            'producto',
            'categoria',
            'stock_actual',
            'limite_minimo',
            'demanda_proyectada',
            'dias_proyectados',
            'deficit',
            'leida',
            'fecha_creacion',
        ]
        read_only_fields = fields

    def get_deficit(self, obj):
        if obj.demanda_proyectada is not None:
            return max(0, obj.demanda_proyectada - obj.stock_actual)
        return max(0, obj.limite_minimo - obj.stock_actual)
