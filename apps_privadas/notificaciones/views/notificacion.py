from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from apps_privadas.notificaciones.models import Notificacion
from apps_privadas.notificaciones.serializers import (
    NotificacionSerializer,
    SuscribirNotificacionSerializer,
)
from apps_privadas.notificaciones.services import NotificacionService


class NotificacionViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'vapid_public_key':
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Notificacion.objects.select_related('usuario', 'ultima_promocion')
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        return queryset.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == 'suscribirse':
            return SuscribirNotificacionSerializer
        return NotificacionSerializer

    @action(detail=False, methods=['post'])
    def suscribirse(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        keys = serializer.validated_data['keys']
        notificacion = NotificacionService.suscribir_usuario(
            usuario=request.user,
            endpoint=serializer.validated_data['endpoint'],
            p256dh=keys['p256dh'],
            auth=keys['auth'],
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response(
            NotificacionSerializer(notificacion).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'])
    def desuscribirse(self, request):
        endpoint = request.data.get('endpoint')
        actualizadas = NotificacionService.desuscribir_usuario(request.user, endpoint=endpoint)
        return Response(
            {
                'success': True,
                'desactivadas': actualizadas,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='vapid-public-key')
    def vapid_public_key(self, request):
        return Response(
            {
                'public_key': getattr(settings, 'VAPID_PUBLIC_KEY', ''),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'])
    def configuracion(self, request):
        suscripciones_activas = Notificacion.objects.filter(
            usuario=request.user,
            activa=True,
        ).count()

        return Response(
            {
                **NotificacionService.estado_configuracion(),
                'suscripciones_activas_usuario': suscripciones_activas,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'])
    def probar(self, request):
        resultado = NotificacionService.enviar_prueba(
            usuario=request.user,
            titulo=request.data.get('titulo', 'Notificacion de prueba'),
            mensaje=request.data.get('mensaje', 'Las notificaciones push estan funcionando.'),
        )
        http_status = status.HTTP_200_OK if resultado['success'] else status.HTTP_400_BAD_REQUEST
        return Response(resultado, status=http_status)
