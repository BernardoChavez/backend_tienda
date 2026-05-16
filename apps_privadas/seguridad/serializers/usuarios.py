from rest_framework import serializers

from apps_privadas.seguridad.models.usuario import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Usuario"""

    grupos = serializers.SerializerMethodField()
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nombre', 'apellido', 'fecha_nacimiento',
                  'grupos', 'nombre_completo', 'is_active', 'is_superuser', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'grupos', 'nombre_completo']

    def get_grupos(self, obj):
        """Retorna los nombres de los grupos del usuario"""
        return list(obj.groups.values_list('name', flat=True))


class CrearUsuarioSerializer(serializers.Serializer):
    """Serializer para crear usuarios (solo username, password y grupo)"""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    grupo_id = serializers.IntegerField()
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_username(self, value):
        """Validar que username sea unico (solo en usuarios activos)"""
        if Usuario.objects.filter(username=value, is_active=True).exists():
            raise serializers.ValidationError(f"El usuario {value} ya existe")
        return value


class ActualizarUsuarioSerializer(serializers.Serializer):
    """Serializer para actualizar usuarios"""

    password = serializers.CharField(write_only=True, min_length=8, required=False)
    grupo_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True)


class RegistrarClienteSerializer(serializers.Serializer):
    """Serializer para registrar clientes"""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    fecha_nacimiento = serializers.DateField()

    def validate_username(self, value):
        """Validar que username sea unico (solo en usuarios activos)"""
        if Usuario.objects.filter(username=value, is_active=True).exists():
            raise serializers.ValidationError(f"El usuario {value} ya existe")
        return value

