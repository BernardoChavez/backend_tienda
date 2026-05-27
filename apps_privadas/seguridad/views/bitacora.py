from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps_privadas.seguridad.models.bitacora_auditoria import BitacoraAuditoria
from apps_privadas.seguridad.permissions import HasModelPermission
from apps_privadas.seguridad.serializers.bitacora import BitacoraAuditoriaSerializer


class BitacoraAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Consulta de bitacora de auditoria.

    Endpoints:
    - GET /api/bitacora/ - Listar eventos de auditoria
    - GET /api/bitacora/{id_bitacora}/ - Ver detalle de un evento

    Filtros por query params:
    - fecha_desde=YYYY-MM-DD
    - fecha_hasta=YYYY-MM-DD
    - usuarios_id=1
    - entidad=usuario
    - accion=crear
    - metodo=POST
    - estado_http=200
    - buscar=texto
    """

    queryset = BitacoraAuditoria.objects.all()
    serializer_class = BitacoraAuditoriaSerializer
    permission_classes = [IsAuthenticated, HasModelPermission]
    lookup_field = 'id_bitacora'

    def get_queryset(self):
        queryset = super().get_queryset()

        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        usuarios_id = self.request.query_params.get('usuarios_id')
        entidad = self.request.query_params.get('entidad')
        accion = self.request.query_params.get('accion')
        metodo = self.request.query_params.get('metodo')
        estado_http = self.request.query_params.get('estado_http')
        buscar = self.request.query_params.get('buscar')

        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        if usuarios_id:
            queryset = queryset.filter(usuarios_id=usuarios_id)
        if entidad:
            queryset = queryset.filter(entidad__icontains=entidad)
        if accion:
            queryset = queryset.filter(accion__icontains=accion)
        if metodo:
            queryset = queryset.filter(metodo__iexact=metodo)
        if estado_http:
            queryset = queryset.filter(estado_http=estado_http)
        if buscar:
            queryset = queryset.filter(detalles__icontains=buscar)

        return queryset

