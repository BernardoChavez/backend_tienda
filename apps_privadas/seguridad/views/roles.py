from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import Group

from apps_privadas.seguridad.permissions import HasModelPermission
from apps_privadas.seguridad.serializers.roles import (
    RolListSerializer,
    RolCrearSerializer,
    RolActualizarSerializer,
)
from apps_privadas.seguridad.services.roles import RolService
from apps_privadas.seguridad.services.permisos import PermisoService


class RolViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar roles.

    Endpoints:
    - GET /api/roles/ - Listar roles
    - POST /api/roles/ - Crear rol
    - GET /api/roles/{id}/ - Obtener rol
    - PUT /api/roles/{id}/ - Actualizar rol
    - DELETE /api/roles/{id}/ - Eliminar rol
    - GET /api/roles/permisos/disponibles/ - Listar permisos disponibles
    - GET /api/roles/permisos/por_app/ - Permisos agrupados por app
    """

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, HasModelPermission]

    def get_serializer_class(self):
        """Retorna el serializer segun la accion"""
        if self.action == 'create':
            return RolCrearSerializer
        if self.action in ['update', 'partial_update']:
            return RolActualizarSerializer
        return RolListSerializer

    @action(detail=False, methods=['get'])
    def permisos_disponibles(self, request):
        """
        Retorna todos los permisos disponibles.

        Respuesta:
        [
            {
                "id": 1,
                "nombre": "Can add user",
                "codigo": "add_user",
                "app": "auth",
                "modelo": "user"
            }
        ]
        """
        permisos = PermisoService.obtener_permisos_disponibles()
        return Response(permisos, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def permisos_por_app(self, request):
        """
        Retorna permisos agrupados por aplicacion.

        Respuesta:
        {
            "auth": [...],
            "seguridad": [...]
        }
        """
        permisos = PermisoService.obtener_permisos_por_app()
        return Response(permisos, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo rol.

        Body:
        {
            "name": "Vendedores",
            "permisos_ids": [1, 2, 3]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nombre = serializer.validated_data['name']
        permisos_ids = serializer.validated_data.get('permisos_ids', [])

        resultado = RolService.crear_rol(nombre, [p.id for p in permisos_ids])

        if resultado['success']:
            rol = Group.objects.get(id=resultado['rol_id'])
            serializer = RolListSerializer(rol)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {'error': resultado['error']},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """
        Actualizar un rol.

        Body:
        {
            "name": "Vendedores Premium",
            "permisos_ids": [1, 2, 3, 4]
        }
        """
        rol = self.get_object()
        serializer = self.get_serializer(rol, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        nombre = serializer.validated_data.get('name')
        permisos_ids = serializer.validated_data.get('permisos_ids')

        permisos_ids_lista = [p.id for p in permisos_ids] if permisos_ids is not None else None

        resultado = RolService.actualizar_rol(
            rol.id,
            nombre=nombre,
            permisos_ids=permisos_ids_lista
        )

        if resultado['success']:
            rol_actualizado = Group.objects.get(id=rol.id)
            serializer = RolListSerializer(rol_actualizado)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {'error': resultado['error']},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Eliminar un rol"""
        rol = self.get_object()

        resultado = RolService.eliminar_rol(rol.id)

        if resultado['success']:
            return Response(
                {'mensaje': resultado['mensaje']},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'error': resultado['error']},
            status=status.HTTP_400_BAD_REQUEST
        )
