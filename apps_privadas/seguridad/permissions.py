"""
Permisos genéricos para validación automática basada en modelos y acciones.

Estas clases de permisos usan el sistema de permisos de Django para validar
automáticamente si un usuario tiene permiso para realizar una acción.
"""

from rest_framework.permissions import BasePermission


class HasModelPermission(BasePermission):
    """
    Valida automáticamente el permiso basado en:
    - El modelo del ViewSet (app.modelo)
    - La acción que se ejecuta (create, update, delete, etc)

    Mapeo de acciones a permisos Django:
    - create/POST → add_<modelo>
    - update/PUT → change_<modelo>
    - partial_update/PATCH → change_<modelo>
    - destroy/DELETE → delete_<modelo>
    - list/GET (todas) → view_<modelo>
    - retrieve/GET (detalle) → view_<modelo>

    Ejemplo:
    - ProductoViewSet + action='create' → requiere 'inventario.add_producto'
    - UsuarioViewSet + action='update' → requiere 'seguridad.change_usuario'
    - CategoriaViewSet + action='destroy' → requiere 'inventario.delete_categoria'
    """

    # Mapeo de acciones HTTP a tipos de permiso Django
    ACTION_TO_PERMISSION_TYPE = {
        'create': 'add',
        'list': 'view',
        'retrieve': 'view',
        'update': 'change',
        'partial_update': 'change',
        'destroy': 'delete'
    }

    def has_permission(self, request, view):
        """
        Verifica si el usuario tiene el permiso requerido para la acción.

        Args:
            request: La solicitud HTTP
            view: El ViewSet o view que está siendo accedido

        Returns:
            True si el usuario tiene permiso, False si no
        """
        # Obtener la acción (create, update, list, etc)
        action = getattr(view, 'action', None)

        if not action:
            # Si no hay acción definida, permitir (probablemente no es un ViewSet)
            return True

        # Obtener el tipo de permiso (add, change, delete, view)
        permission_type = self.ACTION_TO_PERMISSION_TYPE.get(action, 'change')

        # Obtener el modelo del ViewSet
        queryset = getattr(view, 'queryset', None)
        if not queryset:
            # Si no hay queryset, no podemos determinar el permiso
            return True

        model = queryset.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        # Construir el código de permiso
        # Ejemplo: 'inventario.change_producto'
        permission_code = f'{app_label}.{permission_type}_{model_name}'

        # Validar que el usuario tenga el permiso
        has_perm = request.user.has_perm(permission_code)

        return has_perm


class IsAdminUser(BasePermission):
    """
    Permite solo si el usuario es superusuario (admin).
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsStaffUser(BasePermission):
    """
    Permite solo si el usuario es staff.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

