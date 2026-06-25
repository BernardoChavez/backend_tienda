from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps_privadas.seguridad.services.auditoria import registrar_bitacora


class AuditoriaMiddleware(MiddlewareMixin):
    """Registra automaticamente las acciones realizadas contra la API."""

    EXCLUDED_PREFIXES = (
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',
        '/api/login/',
    )

    ACTION_BY_METHOD = {
        'GET': 'CONSULTAR',
        'POST': 'CREAR',
        'PUT': 'ACTUALIZAR',
        'PATCH': 'ACTUALIZAR',
        'DELETE': 'ELIMINAR',
    }

    def process_response(self, request, response):
        if not self._should_audit(request):
            return response

        usuario = self._get_usuario(request)
        accion = self._get_accion(request)
        entidad = self._get_entidad(request)
        detalles = self._get_detalles(request, response)

        registrar_bitacora(
            usuario_id=getattr(usuario, 'id', 0) if usuario else 0,
            usuario_username=getattr(usuario, 'username', None) if usuario else None,
            entidad=entidad,
            accion=accion,
            detalles=detalles,
            metodo=request.method,
            ruta=request.path,
            ip_cliente=self._get_client_ip(request),
            estado_http=getattr(response, 'status_code', None),
        )
        return response

    def _should_audit(self, request):
        if not request.path.startswith('/api/') and not request.path.startswith('/admin/'):
            return False
        if request.method in ['OPTIONS', 'HEAD']:
            return False
        return not any(request.path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES)

    def _get_usuario(self, request):
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            return user

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.lower().startswith('bearer '):
            return None

        try:
            jwt_auth = JWTAuthentication()
            raw_token = auth_header.split(' ', 1)[1].strip()
            validated_token = jwt_auth.get_validated_token(raw_token)
            return jwt_auth.get_user(validated_token)
        except Exception:
            return None

    def _get_accion(self, request):
        path = request.path.strip('/').lower()
        if path.endswith('login'):
            return 'LOGIN'
        if 'recuperar-password' in path:
            return 'RECUPERAR_PASSWORD'
        return self.ACTION_BY_METHOD.get(request.method, request.method)

    def _get_entidad(self, request):
        resolver_match = getattr(request, 'resolver_match', None)
        if resolver_match and resolver_match.view_name:
            return resolver_match.view_name[:100]

        partes = [parte for parte in request.path.strip('/').split('/') if parte]
        if len(partes) >= 2:
            return f"api.{partes[1]}"[:100]
        return 'api'

    def _get_detalles(self, request, response):
        query = request.META.get('QUERY_STRING', '')
        status_code = getattr(response, 'status_code', '')
        if query:
            return f"{request.method} {request.path}?{query} -> {status_code}"
        return f"{request.method} {request.path} -> {status_code}"

    def _get_client_ip(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
