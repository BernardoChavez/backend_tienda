from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group, Permission

from apps_privadas.seguridad.models import Usuario
from apps_privadas.seguridad.serializers import (
    UsuarioSerializer,
    CrearUsuarioSerializer,
    ActualizarUsuarioSerializer,
    RegistrarClienteSerializer,
    RolListSerializer,
    RolCrearSerializer,
    RolActualizarSerializer,
    PermisoSerializer
)
from apps_privadas.seguridad.login_serializers import LoginSerializer
from apps_privadas.seguridad.services import UsuarioService, ClienteService, RolService, PermisoService


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Endpoint de login para autenticar usuarios.

    Body (JSON):
    {
        "username": "usuario",
        "password": "contraseña"
    }

    Respuesta exitosa (200):
    {
        "success": true,
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "usuario_id": 1,
        "username": "usuario",
        "nombre_completo": "Juan Pérez"
    }

    Respuesta error (400):
    {
        "success": false,
        "error": "Usuario o contraseña incorrectos"
    }
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        usuario = serializer.validated_data['usuario']

        # Generar tokens JWT
        refresh = RefreshToken.for_user(usuario)

        # Agregar información personalizada a los tokens
        refresh['usuario_id'] = usuario.id
        refresh['username'] = usuario.username
        refresh['nombre_completo'] = usuario.nombre_completo

        access = refresh.access_token
        access['usuario_id'] = usuario.id
        access['username'] = usuario.username
        access['nombre_completo'] = usuario.nombre_completo

        print(f"✓ Login exitoso: {usuario.username} (ID: {usuario.id})")

        return Response({
            'success': True,
            'access': str(access),
            'refresh': str(refresh),
            'usuario_id': usuario.id,
            'username': usuario.username,
            'nombre_completo': usuario.nombre_completo
        }, status=status.HTTP_200_OK)

    else:
        print(f"✗ Login fallido: {serializer.errors}")
        return Response({
            'success': False,
            'error': serializer.errors.get('non_field_errors', ['Error desconocido'])[0]
            if serializer.errors.get('non_field_errors')
            else list(serializer.errors.values())[0][0] if serializer.errors else 'Error desconocido'
        }, status=status.HTTP_400_BAD_REQUEST)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de usuarios.

    Endpoints:
    - GET /api/usuarios/ - Listar usuarios
    - GET /api/usuarios/{id}/ - Obtener usuario
    - POST /api/usuarios/ - Crear usuario (requiere grupo obligatorio)
    - PUT /api/usuarios/{id}/ - Actualizar usuario
    - DELETE /api/usuarios/{id}/ - Eliminar usuario
    - POST /api/usuarios/registrar_cliente/ - Registrar cliente (sin autenticación)
    """

    queryset = Usuario.objects.filter(is_active=True)
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Retorna el serializer según la acción"""
        if self.action == 'create':
            return CrearUsuarioSerializer
        elif self.action == 'partial_update' or self.action == 'update':
            return ActualizarUsuarioSerializer
        elif self.action == 'registrar_cliente':
            return RegistrarClienteSerializer
        return UsuarioSerializer

    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action == 'registrar_cliente':
            permission_classes = [AllowAny]  # Registro público
        else:
            permission_classes = [IsAuthenticated]

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
            grupo_id=serializer.validated_data['grupo_id']
        )

        if resultado['success']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        else:
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
            grupo_id=serializer.validated_data.get('grupo_id')
        )

        if resultado['success']:
            usuario = UsuarioService.obtener_usuario(pk)
            return Response(usuario, status=status.HTTP_200_OK)
        else:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        """Actualización parcial de usuario"""
        return self.update(request, pk, *args, **kwargs)

    def retrieve(self, request, pk=None):
        """
        Obtener un usuario por ID.

        Respuesta:
        {
            "id": 1,
            "username": "juan_perez",
            "nombre": "Juan",
            "apellido": "Pérez",
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

        Respuesta: Array de usuarios
        """
        usuarios = UsuarioService.listar_usuarios()
        return Response(usuarios, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Eliminar (desactivar) un usuario.
        """
        resultado = UsuarioService.eliminar_usuario(pk)

        if resultado['success']:
            return Response(resultado, status=status.HTTP_200_OK)
        else:
            return Response(resultado, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registrar_cliente(self, request):
        """
        Registrar un nuevo cliente (sin autenticación requerida).

        Body (JSON):
        {
            "username": "cliente123",
            "password": "MiPassword123!",
            "nombre": "Juan",
            "apellido": "Pérez",
            "fecha_nacimiento": "1990-01-15"
        }

        El grupo será automáticamente "Cliente".
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
        else:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# VIEWSET PARA ROLES
# ============================================================================

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
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Retorna el serializer según la acción"""
        if self.action == 'create':
            return RolCrearSerializer
        elif self.action in ['update', 'partial_update']:
            return RolActualizarSerializer
        else:
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
        Retorna permisos agrupados por aplicación.
        
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
        else:
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
        
        permisos_ids_lista = [p.id for p in permisos_ids] if permisos_ids else None
        
        resultado = RolService.actualizar_rol(
            rol.id,
            nombre=nombre,
            permisos_ids=permisos_ids_lista
        )
        
        if resultado['success']:
            rol_actualizado = Group.objects.get(id=rol.id)
            serializer = RolListSerializer(rol_actualizado)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
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
        else:
            return Response(
                {'error': resultado['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
