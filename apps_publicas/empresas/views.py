from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps_publicas.empresas.models import Empresa, Dominio, Plan, Suscripcion
from apps_publicas.empresas.serializers import (
    EmpresaRegistroSerializer,
    EmpresaCreatedSerializer,
    PlanSerializer,
    SuscripcionSerializer,
    SuscripcionCambioSerializer,
)
from apps_publicas.empresas.services import (
    EmpresaRegistroService,
    EmpresaListaService,
    PlanService,
    SuscripcionService,
    SuscripcionCambioService,
)
from apps_privadas.seguridad.permissions import HasModelPermission


class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar empresas.

    Endpoints:
    - POST /api/empresas/register/ - Registrar nueva empresa
    - GET /api/empresas/ - Listar todas las empresas
    - GET /api/empresas/{id}/ - Obtener empresa específica
    """

    queryset = Empresa.objects.filter(is_active=True)
    permission_classes = [AllowAny]  # En producción, cambiar a IsAuthenticated

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registrar(self, request):
        """
        Endpoint para registrar una nueva empresa.

        Body JSON esperado:
        {
            "nombre": "Mi Tienda",
            "correo": "info@mitienda.com",
            "super_admin": {
                "username": "admin",
                "email": "admin@mitienda.com",
                "password": "Contraseña123!",
                "password_confirm": "Contraseña123!"
            }
        }

        Respuesta exitosa (201):
        {
            "success": true,
            "empresa_id": 1,
            "nombre": "Mi Tienda",
            "schema_name": "mi_tienda",
            "dominio": "mi-tienda.localhost",
            "super_admin_username": "admin",
            "mensaje": "Empresa creada..."
        }

        Respuesta de error (400):
        {
            "success": false,
            "errors": {
                "nombre": ["El nombre solo puede contener..."],
                "super_admin": {
                    "password": ["Las contraseñas no coinciden"]
                }
            }
        }
        """

        serializer = EmpresaRegistroSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener datos validados
        nombre = serializer.validated_data['nombre']
        correo = serializer.validated_data['correo']
        plan = serializer.validated_data['plan']
        ciclo = serializer.validated_data['ciclo']
        super_admin_data = serializer.validated_data['super_admin']

        # Remover password_confirm ya que no lo necesitamos
        super_admin_data.pop('password_confirm', None)

        # Crear empresa con el servicio
        resultado = EmpresaRegistroService.crear_empresa_con_admin(
            nombre,
            correo,
            super_admin_data,
            plan,
            ciclo
        )

        if resultado['success']:
            response_serializer = EmpresaCreatedSerializer(resultado)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': resultado.get('error', 'Error desconocido')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def listar_todas(self, request):
        """
        Endpoint para listar todas las empresas activas.

        Respuesta:
        [
            {
                "id": 1,
                "nombre": "Tienda Amiga",
                "correo": "info@tienda-amiga.com",
                "schema_name": "tienda_amiga",
                "fecha_creacion": "2024-04-07T10:30:00Z"
            }
        ]
        """
        empresas = EmpresaListaService.obtener_todas_empresas()
        return Response(empresas, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Obtener información detallada de una empresa específica.

        Respuesta:
        {
            "id": 1,
            "nombre": "Tienda Amiga",
            "correo": "info@tienda-amiga.com",
            "schema_name": "tienda_amiga",
            "dominio": "tienda-amiga.localhost",
            "fecha_creacion": "2024-04-07T10:30:00Z"
        }
        """
        empresa = EmpresaListaService.obtener_empresa_por_id(pk)

        if empresa is None:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(empresa, status=status.HTTP_200_OK)


class PlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar planes.

    Endpoints:
    - GET /api/planes/ - Listar todos los planes
    - POST /api/planes/ - Crear un nuevo plan
    - GET /api/planes/{id}/ - Obtener detalles de un plan específico
    - PUT /api/planes/{id}/ - Actualizar un plan existente
    - DELETE /api/planes/{id}/ - Eliminar un plan
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated, HasModelPermission]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), HasModelPermission()]

    def get_queryset(self):
        activos = self.request.query_params.get('activos')
        if activos in ['1', 'true', 'True']:
            return PlanService.listar_planes(activos_only=True)
        return PlanService.listar_planes(activos_only=False)

    def perform_create(self, serializer):
        PlanService.crear_plan(serializer.validated_data)

    def perform_update(self, serializer):
        PlanService.actualizar_plan(serializer.instance, serializer.validated_data)

    def perform_destroy(self, instance):
        PlanService.eliminar_plan(instance)


class SuscripcionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar suscripciones.

    Endpoints:
    - GET /api/suscripciones/ - Listar todas las suscripciones
    - POST /api/suscripciones/ - Crear una nueva suscripción
    - GET /api/suscripciones/{id}/ - Obtener detalles de una suscripción específica
    - PUT /api/suscripciones/{id}/ - Actualizar una suscripción existente
    - DELETE /api/suscripciones/{id}/ - Eliminar una suscripción
    """

    queryset = Suscripcion.objects.select_related('empresa', 'plan')
    serializer_class = SuscripcionSerializer
    permission_classes = [IsAuthenticated, HasModelPermission]

    def perform_create(self, serializer):
        try:
            SuscripcionService.crear_suscripcion(serializer.validated_data)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

    def perform_update(self, serializer):
        try:
            SuscripcionService.actualizar_suscripcion(serializer.instance, serializer.validated_data)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        instancia = self.get_object()
        cancelada_por = request.data.get('cancelada_por', '')
        motivo = request.data.get('motivo', '')
        SuscripcionService.cancelar_suscripcion(instancia, cancelada_por=cancelada_por, motivo=motivo)
        serializer = self.get_serializer(instancia)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def renovar(self, request, pk=None):
        instancia = self.get_object()
        renovada_por = request.data.get('renovada_por', '')
        motivo = request.data.get('motivo', '')
        SuscripcionService.renovar_suscripcion(instancia, renovada_por=renovada_por, motivo=motivo)
        serializer = self.get_serializer(instancia)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SuscripcionCambioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar historial de cambios de suscripcion.

    Endpoints:
    - GET /api/suscripcion-cambios/ - Listar cambios
    - GET /api/suscripcion-cambios/{id}/ - Detalle de un cambio
    """

    queryset = SuscripcionCambioService.listar_cambios()
    serializer_class = SuscripcionCambioSerializer
    permission_classes = [IsAuthenticated, HasModelPermission]

    def get_queryset(self):
        suscripcion_id = self.request.query_params.get('suscripcion_id')
        return SuscripcionCambioService.listar_cambios(suscripcion_id=suscripcion_id)

