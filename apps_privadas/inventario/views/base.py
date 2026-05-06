from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps_privadas.seguridad.permissions import HasModelPermission


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasModelPermission]
    model = None
    serializer_class = None
    crear_serializer_class = None
    actualizar_serializer_class = None
    service_class = None

    def get_serializer_class(self):
        if self.action == 'create':
            return self.crear_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.actualizar_serializer_class
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        instance = self.model.objects.create(**data)
        
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
