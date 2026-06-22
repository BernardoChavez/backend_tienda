from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps_privadas.inventario.models import Producto
from apps_privadas.notificaciones.models import Promocion
from apps_privadas.notificaciones.serializers import (
    ActualizarPromocionSerializer,
    CrearPromocionSerializer,
    PromocionSerializer,
)
from apps_privadas.notificaciones.services import NotificacionService


class PromocionViewSet(viewsets.ModelViewSet):
    queryset = Promocion.objects.select_related('producto', 'creado_por').all()
    serializer_class = PromocionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearPromocionSerializer
        if self.action in ['update', 'partial_update']:
            return ActualizarPromocionSerializer
        return PromocionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        producto = Producto.objects.get(id=data.pop('producto_id'))
        promocion = Promocion.objects.create(
            producto=producto,
            creado_por=request.user,
            **data,
        )

        return Response(
            PromocionSerializer(promocion).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        promocion = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        producto_id = data.pop('producto_id', None)
        if producto_id:
            data['producto'] = Producto.objects.get(id=producto_id)

        for key, value in data.items():
            setattr(promocion, key, value)
        promocion.save()

        return Response(PromocionSerializer(promocion).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        promocion = self.get_object()
        resultado = NotificacionService.publicar_promocion(promocion, request.user, request=request)
        http_status = status.HTTP_200_OK if resultado['success'] else status.HTTP_400_BAD_REQUEST
        return Response(resultado, status=http_status)

