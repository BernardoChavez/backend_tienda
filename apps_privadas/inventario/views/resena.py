from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps_privadas.inventario.models.resena import Resena
from apps_privadas.inventario.serializers.resena import (
    ActualizarResenaSerializer,
    CrearResenaSerializer,
    ResenaSerializer,
)
from apps_privadas.inventario.services.resena import ResenaService


class ResenaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearResenaSerializer
        if self.action in ['update', 'partial_update']:
            return ActualizarResenaSerializer
        return ResenaSerializer

    def get_queryset(self):
        queryset = Resena.objects.select_related('usuario', 'producto')
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = ResenaService.crear_resena(
            usuario=request.user,
            producto_id=serializer.validated_data['producto_id'],
            calificacion=serializer.validated_data['calificacion'],
            comentario=serializer.validated_data.get('comentario', ''),
        )

        if not resultado['success']:
            return Response({'detail': resultado['error']}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ResenaSerializer(resultado['resena']).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        resena = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = ResenaService.actualizar_resena(
            resena=resena,
            usuario=request.user,
            calificacion=serializer.validated_data.get('calificacion'),
            comentario=serializer.validated_data.get('comentario'),
        )

        if not resultado['success']:
            return Response({'detail': resultado['error']}, status=status.HTTP_403_FORBIDDEN)

        return Response(ResenaSerializer(resultado['resena']).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        resena = self.get_object()
        resultado = ResenaService.eliminar_resena(resena=resena, usuario=request.user)

        if not resultado['success']:
            return Response({'detail': resultado['error']}, status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)