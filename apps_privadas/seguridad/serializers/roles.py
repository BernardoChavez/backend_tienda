from rest_framework import serializers
from django.contrib.auth.models import Group, Permission


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
        if not instance and Group.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Ya existe un rol con el nombre '{value}'")
        return value

    def update(self, instance, validated_data):
        permisos = validated_data.pop('permisos_ids', None)

        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if permisos is not None:
            instance.permissions.set(permisos)

        return instance

