from rest_framework import serializers

from apps_privadas.notificaciones.models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    ultima_promocion_titulo = serializers.CharField(source='ultima_promocion.titulo', read_only=True)

    class Meta:
        model = Notificacion
        fields = [
            'id',
            'usuario',
            'usuario_username',
            'endpoint',
            'p256dh',
            'auth',
            'user_agent',
            'activa',
            'ultima_promocion',
            'ultima_promocion_titulo',
            'ultimo_envio',
            'ultimo_error',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'usuario',
            'usuario_username',
            'user_agent',
            'ultima_promocion',
            'ultima_promocion_titulo',
            'ultimo_envio',
            'ultimo_error',
            'fecha_creacion',
            'fecha_actualizacion',
        ]


class SuscribirNotificacionSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=1000)
    keys = serializers.DictField(write_only=True)

    def validate_keys(self, value):
        if not value.get('p256dh'):
            raise serializers.ValidationError('La clave p256dh es requerida.')
        if not value.get('auth'):
            raise serializers.ValidationError('La clave auth es requerida.')
        return value

