from rest_framework import serializers

from apps_privadas.seguridad.models.bitacora_auditoria import BitacoraAuditoria


class BitacoraAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para consultar la bitacora de auditoria."""

    class Meta:
        model = BitacoraAuditoria
        fields = [
            'id_bitacora',
            'fecha',
            'hora',
            'entidad',
            'detalles',
            'accion',
            'usuarios_id',
        ]
        read_only_fields = fields
