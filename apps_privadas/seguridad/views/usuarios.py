from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps_privadas.seguridad.models.usuario import Usuario
from apps_privadas.seguridad.permissions import HasModelPermission
from apps_privadas.seguridad.serializers.usuarios import (
    UsuarioSerializer,
    CrearUsuarioSerializer,
    ActualizarUsuarioSerializer,
    RegistrarClienteSerializer,
)
from apps_privadas.seguridad.services.usuarios import UsuarioService
from apps_privadas.seguridad.services.clientes import ClienteService


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de usuarios.

    Endpoints:
    - GET /api/usuarios/ - Listar usuarios
    - GET /api/usuarios/{id}/ - Obtener usuario
    - POST /api/usuarios/ - Crear usuario (requiere grupo obligatorio)
    - PUT /api/usuarios/{id}/ - Actualizar usuario
    - DELETE /api/usuarios/{id}/ - Eliminar usuario
    - POST /api/usuarios/registrar_cliente/ - Registrar cliente (sin autenticacion)
    """

    queryset = Usuario.objects.filter(is_active=True)
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, HasModelPermission]

    def get_serializer_class(self):
        """Retorna el serializer segun la accion"""
        if self.action == 'create':
            return CrearUsuarioSerializer
        if self.action in ['partial_update', 'update']:
            return ActualizarUsuarioSerializer
        if self.action == 'registrar_cliente':
            return RegistrarClienteSerializer
        return UsuarioSerializer

    def get_permissions(self):
        """Define permisos segun la accion"""
        if self.action == 'registrar_cliente':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, HasModelPermission]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo usuario.

        Body (JSON):
        {
            "username": "juan_perez",
            "password": "MiPassword123!",
            "grupo_id": 1
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = UsuarioService.crear_usuario(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            grupo_id=serializer.validated_data['grupo_id'],
            email=serializer.validated_data.get('email')
        )

        if resultado['success']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Actualizar un usuario.

        Body (JSON):
        {
            "password": "NuevaPassword123!",
            "grupo_id": 2
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = UsuarioService.actualizar_usuario(
            usuario_id=pk,
            password=serializer.validated_data.get('password'),
            grupo_id=serializer.validated_data.get('grupo_id'),
            email=serializer.validated_data.get('email')
        )

        if resultado['success']:
            usuario = UsuarioService.obtener_usuario(pk)
            return Response(usuario, status=status.HTTP_200_OK)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        """Actualizacion parcial de usuario"""
        return self.update(request, pk, *args, **kwargs)

    def retrieve(self, request, pk=None):
        """
        Obtener un usuario por ID.

        Respuesta:
        {
            "id": 1,
            "username": "juan_perez",
            "nombre": "Juan",
            "apellido": "Perez",
            "grupos": ["Vendedor"],
            ...
        }
        """
        usuario = UsuarioService.obtener_usuario(pk)

        if usuario is None:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(usuario, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        Listar todos los usuarios.

        Respuesta: Array de usuarios paginado
        """
        usuarios_data = UsuarioService.listar_usuarios()

        # Aplicar paginacion
        page = self.paginate_queryset(usuarios_data)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(usuarios_data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Eliminar (desactivar) un usuario.
        """
        resultado = UsuarioService.eliminar_usuario(pk)

        if resultado['success']:
            return Response(resultado, status=status.HTTP_200_OK)
        return Response(resultado, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registrar_cliente(self, request):
        """
        Registrar un nuevo cliente (sin autenticacion requerida).

        Body (JSON):
        {
            "username": "cliente123",
            "password": "MiPassword123!",
            "nombre": "Juan",
            "apellido": "Perez",
            "fecha_nacimiento": "1990-01-15"
        }

        El grupo sera automaticamente "Cliente".
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = ClienteService.registrar_cliente(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            nombre=serializer.validated_data['nombre'],
            apellido=serializer.validated_data['apellido'],
            fecha_nacimiento=serializer.validated_data['fecha_nacimiento']
        )

        if resultado['success']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

