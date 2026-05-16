from django.contrib.auth.models import Permission


class PermisoService:
    """Servicio para obtener permisos disponibles"""

    @staticmethod
    def obtener_permisos_disponibles():
        """Obtiene todos los permisos disponibles"""
        permisos = Permission.objects.all()

        resultado = []
        for permiso in permisos:
            resultado.append({
                'id': permiso.id,
                'nombre': permiso.name,
                'codigo': permiso.codename,
                'app': permiso.content_type.app_label,
                'modelo': permiso.content_type.model
            })

        return resultado

    @staticmethod
    def obtener_permisos_por_app():
        """Obtiene permisos agrupados por aplicacion"""
        permisos = Permission.objects.all().select_related('content_type')

        resultado = {}
        for permiso in permisos:
            app = permiso.content_type.app_label

            if app not in resultado:
                resultado[app] = []

            resultado[app].append({
                'id': permiso.id,
                'nombre': permiso.name,
                'codigo': permiso.codename,
                'modelo': permiso.content_type.model
            })

        return resultado

