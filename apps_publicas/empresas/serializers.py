from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps_publicas.empresas.models import Empresa, Dominio, Plan, Suscripcion, CicloSuscripcion, SuscripcionCambio

User = get_user_model()


class SuperAdminSerializer(serializers.Serializer):
    """Serializer para los datos del super admin de la empresa"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """Validar que las contraseñas coincidan"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Las contraseñas no coinciden.'
            })
        return data


class EmpresaRegistroSerializer(serializers.Serializer):
    """Serializer para registro completo de empresa + super admin"""

    # Datos de la empresa
    nombre = serializers.CharField(max_length=100)
    correo = serializers.EmailField()

    # Datos del plan inicial
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.filter(activo=True))
    ciclo = serializers.ChoiceField(choices=CicloSuscripcion.choices, default=CicloSuscripcion.MENSUAL)

    # Datos del super admin
    super_admin = SuperAdminSerializer()

    def validate_nombre(self, value):
        """Validar que el nombre sea único y no contenga caracteres especiales"""
        if Empresa.objects.filter(nombre=value).exists():
            raise serializers.ValidationError(
                f"Ya existe una empresa con el nombre '{value}'."
            )

        # Validar que solo contenga letras, números y espacios
        if not all(c.isalnum() or c.isspace() for c in value):
            raise serializers.ValidationError(
                "El nombre solo puede contener letras, números y espacios."
            )
        return value

    def validate_correo(self, value):
        """Validar que el correo sea único"""
        if Empresa.objects.filter(correo=value).exists():
            raise serializers.ValidationError(
                f"Ya existe una empresa registrada con el correo '{value}'."
            )
        return value

    def validate_super_admin(self, value):
        """Validar datos del super admin"""
        # Nota: No validamos username único globalmente porque cada tenant
        # tiene su propio schema con sus propios usuarios.
        # El usuario "admin" puede existir en tienda_amiga y en otro tenant sin problema.

        username = value.get('username')

        # Solo validar que username no esté vacío
        if not username or len(username) < 3:
            raise serializers.ValidationError({
                'username': 'El username debe tener al menos 3 caracteres.'
            })

        return value


class EmpresaCreatedSerializer(serializers.Serializer):
    """Serializer para la respuesta de creación de empresa"""
    empresa_id = serializers.IntegerField()
    nombre = serializers.CharField()
    schema_name = serializers.CharField()
    dominio = serializers.CharField()
    super_admin_username = serializers.CharField()
    mensaje = serializers.CharField()


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio_mensual',
            'precio_anual',
            'activo',
            'limite_usuarios',
            'limite_productos',
            'limite_clientes',
            'limite_proveedores',
            'feature_realidad_aumentada',
            'feature_fotos_3d',
            'feature_reportes_dinamicos',
            'feature_backup_automatico',
        ]


class SuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = [
            'id',
            'empresa',
            'plan',
            'estado',
            'ciclo',
            'fecha_inicio',
            'fecha_fin',
            'auto_renovar',
            'ultima_renovacion',
            'cancelada_en',
            'cancelada_por',
            'fecha_creacion',
        ]

    def validate_plan(self, value):
        if not value.activo:
            raise serializers.ValidationError('El plan seleccionado no está activo.')
        return value


class SuscripcionCambioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuscripcionCambio
        fields = [
            'id',
            'suscripcion',
            'plan_anterior',
            'plan_nuevo',
            'cambiado_en',
            'motivo',
        ]


class EmpresaPanelSerializer(serializers.ModelSerializer):
    subdominio = serializers.SerializerMethodField()
    suscripcion_actual = serializers.SerializerMethodField()

    class Meta:
        model = Empresa
        fields = [
            'id',
            'nombre',
            'correo',
            'subdominio',
            'is_active',
            'fecha_creacion',
            'suscripcion_actual',
        ]

    def get_subdominio(self, obj):
        dominio = Dominio.objects.filter(tenant=obj, is_primary=True).first()
        return dominio.domain if dominio else None

    def get_suscripcion_actual(self, obj):
        suscripcion = (
            obj.suscripciones
            .select_related('plan')
            .filter(estado__in=['activa', 'trial'])
            .order_by('-fecha_creacion')
            .first()
        ) or (
            obj.suscripciones
            .select_related('plan')
            .order_by('-fecha_creacion')
            .first()
        )
        if not suscripcion:
            return None
        return {
            'plan_nombre': suscripcion.plan.nombre,
            'plan_precio': (
                suscripcion.plan.precio_anual
                if suscripcion.ciclo == 'anual'
                else suscripcion.plan.precio_mensual
            ),
            'estado': suscripcion.estado,
            'ciclo': suscripcion.ciclo,
            'fecha_inicio': suscripcion.fecha_inicio,
            'fecha_fin': suscripcion.fecha_fin,
        }
