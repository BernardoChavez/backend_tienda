from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Permission

from apps_privadas.seguridad.serializers.login import LoginSerializer
from apps_privadas.seguridad.serializers.recuperacion import (
    SolicitarRecuperacionSerializer,
    VerificarCodigoSerializer,
    CambiarPasswordSerializer,
)
from apps_privadas.seguridad.services.recuperacion_password import RecuperacionPasswordService
from apps_privadas.seguridad.services.auditoria import registrar_bitacora


def _get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Endpoint de login para autenticar usuarios.

    Body (JSON):
    {
        "username": "usuario",
        "password": "contrasena"
    }

    Respuesta exitosa (200):
    {
        "success": true,
        "access": "eyJ0eXAi...",
        "refresh": "eyJ0eXAi...",
        "usuario_id": 1,
        "username": "usuario",
        "nombre_completo": "Juan Perez",
        "is_superuser": false,
        "roles": ["Vendedor"],
        "permisos": ["inventario.view_producto", "inventario.add_producto", ...]
    }

    Respuesta error (400):
    {
        "success": false,
        "error": "Usuario o contrasena incorrectos"
    }
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        usuario = serializer.validated_data['usuario']

        # Generar tokens JWT (sin agregar datos, se mantienen cortos y seguros)
        refresh = RefreshToken.for_user(usuario)
        access = refresh.access_token

        # Obtener roles del usuario
        roles = list(usuario.groups.values_list('name', flat=True))

        # Obtener permisos del usuario
        permisos = []
        if usuario.is_superuser:
            # Si es superuser, tiene todos los permisos
            permisos = ['*']
        else:
            # Obtener permisos del usuario (directos + de grupos)
            permisos = list(
                usuario.user_permissions.values_list('content_type__app_label', 'codename')
            )
            # Agregar permisos de grupos
            permisos += list(
                Permission.objects.filter(
                    group__user=usuario
                ).values_list('content_type__app_label', 'codename').distinct()
            )
            # Formatear como "app.permiso"
            permisos = [f'{app}.{perm}' for app, perm in permisos]
            permisos = list(set(permisos))

        print(f"OK Login exitoso: {usuario.username} (ID: {usuario.id})")
        print(f"  Roles: {roles}")
        print(f"  Permisos: {len(permisos)} permisos")

        registrar_bitacora(
            usuario_id=usuario.id,
            entidad='seguridad.login',
            accion='LOGIN',
            detalles=f"Login exitoso para usuario {usuario.username}",
            metodo=request.method,
            ruta=request.path,
            ip_cliente=_get_client_ip(request),
            estado_http=status.HTTP_200_OK,
        )

        return Response({
            'success': True,
            'access': str(access),
            'refresh': str(refresh),
            'usuario_id': usuario.id,
            'username': usuario.username,
            'nombre_completo': usuario.nombre_completo,
            'is_superuser': usuario.is_superuser,
            'roles': roles,
            'permisos': permisos
        }, status=status.HTTP_200_OK)

    print(f"ERROR Login fallido: {serializer.errors}")
    registrar_bitacora(
        usuario_id=0,
        entidad='seguridad.login',
        accion='LOGIN_FALLIDO',
        detalles=f"Login fallido para usuario {request.data.get('username', '')}",
        metodo=request.method,
        ruta=request.path,
        ip_cliente=_get_client_ip(request),
        estado_http=status.HTTP_400_BAD_REQUEST,
    )
    return Response({
        'success': False,
        'error': serializer.errors.get('non_field_errors', ['Error desconocido'])[0]
        if serializer.errors.get('non_field_errors')
        else list(serializer.errors.values())[0][0] if serializer.errors else 'Error desconocido'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def solicitar_recuperacion(request):
    """
    Paso 1: El usuario ingresa su email para recibir el codigo.

    Body: { "email": "usuario@ejemplo.com" }
    Respuesta: { "success": true, "mensaje": "..." }
    """
    serializer = SolicitarRecuperacionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)

    resultado = RecuperacionPasswordService.solicitar_recuperacion(
        username=serializer.validated_data['username']
    )
    http_status = status.HTTP_200_OK if resultado['success'] else status.HTTP_400_BAD_REQUEST
    return Response(resultado, status=http_status)


@api_view(['POST'])
@permission_classes([AllowAny])
def verificar_codigo(request):
    """
    Paso 2: El usuario ingresa el codigo recibido. El sistema valida si es correcto.

    Body: { "email": "usuario@ejemplo.com", "codigo": "AB12CD34" }
    Respuesta: { "success": true, "mensaje": "Codigo verificado correctamente" }
    """
    serializer = VerificarCodigoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)

    resultado = RecuperacionPasswordService.verificar_codigo(
        username=serializer.validated_data['username'],
        codigo=serializer.validated_data['codigo']
    )
    http_status = status.HTTP_200_OK if resultado['success'] else status.HTTP_400_BAD_REQUEST
    return Response(resultado, status=http_status)


@api_view(['POST'])
@permission_classes([AllowAny])
def cambiar_password(request):
    """
    Paso 3: El usuario ingresa el codigo + nueva contrasena. El sistema actualiza la contrasena.

    Body: { "email": "usuario@ejemplo.com", "codigo": "AB12CD34", "nueva_password": "NuevaPass123!" }
    Respuesta: { "success": true, "mensaje": "Contrasena actualizada correctamente" }
    """
    serializer = CambiarPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'error': list(serializer.errors.values())[0][0]},
                        status=status.HTTP_400_BAD_REQUEST)

    resultado = RecuperacionPasswordService.cambiar_password(
        username=serializer.validated_data['username'],
        codigo=serializer.validated_data['codigo'],
        nueva_password=serializer.validated_data['nueva_password']
    )
    http_status = status.HTTP_200_OK if resultado['success'] else status.HTTP_400_BAD_REQUEST
    return Response(resultado, status=http_status)

