from rest_framework import serializers
from apps_privadas.seguridad.models import Usuario
from django.contrib.auth.models import Group, Permission


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
        """Validar que username sea único (solo en usuarios activos)"""
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
        """Validar que username sea único (solo en usuarios activos)"""
        if Usuario.objects.filter(username=value, is_active=True).exists():
            raise serializers.ValidationError(f"El usuario {value} ya existe")
        return value


# ============================================================================
# SERIALIZERS PARA RECUPERACIÓN DE CONTRASEÑA
# ============================================================================

class SolicitarRecuperacionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)


class VerificarCodigoSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    codigo = serializers.CharField(max_length=8, min_length=6)


class CambiarPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    codigo = serializers.CharField(max_length=8, min_length=6)
    nueva_password = serializers.CharField(write_only=True, min_length=8)


# ============================================================================
# SERIALIZERS PARA ROLES
# ============================================================================

class PermisoSerializer(serializers.ModelSerializer):
    """Serializer para mostrar permisos disponibles"""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class RolListSerializer(serializers.ModelSerializer):
    """Serializer para listar roles con sus permisos"""
    
    permisos = PermisoSerializer(
        source='permissions',
        many=True,
        read_only=True
    )
    cantidad_usuarios = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permisos', 'cantidad_usuarios']
    
    def get_cantidad_usuarios(self, obj):
        return obj.user_set.count()


class RolCrearSerializer(serializers.ModelSerializer):
    """Serializer para crear roles"""
    
    permisos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Group
        fields = ['name', 'permisos_ids']
    
    def create(self, validated_data):
        permisos = validated_data.pop('permisos_ids', [])
        rol = Group.objects.create(**validated_data)
        rol.permissions.set(permisos)
        return rol


class RolActualizarSerializer(serializers.ModelSerializer):
    """Serializer para actualizar roles"""
    
    permisos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Group
        fields = ['name', 'permisos_ids']
        extra_kwargs = {
            'name': {'validators': []}
        }
    
    def validate_name(self, value):
        """Validar que el nombre no exista en otro rol (excluyendo la instancia actual)"""
        instance = self.instance
        if instance and Group.objects.filter(name=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError(f"Ya existe otro rol con el nombre '{value}'")
        elif not instance and Group.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Ya existe un rol con el nombre '{value}'")
        return value

    def update(self, instance, validated_data):
        permisos = validated_data.pop('permisos_ids', None)
        
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        if permisos is not None:
            instance.permissions.set(permisos)
        
        return instance
