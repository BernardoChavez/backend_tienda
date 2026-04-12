from apps_privadas.inventario.views.base import BaseViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from apps_privadas.inventario.models import Producto, Categoria, Multimedio
from apps_privadas.inventario.serializers import (
    ProductoSerializer,
    CrearProductoSerializer,
    ActualizarProductoSerializer
)
from apps_privadas.inventario.cloudinary_service import CloudinaryService


class ProductoViewSet(BaseViewSet):
    queryset = Producto.objects.select_related('categoria').all()
    model = Producto
    serializer_class = ProductoSerializer
    crear_serializer_class = CrearProductoSerializer
    actualizar_serializer_class = ActualizarProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        categoria_id = serializer.validated_data.pop('categoria_id')
        categoria = Categoria.objects.get(id=categoria_id)
        instance = self.model.objects.create(
            categoria=categoria,
            **serializer.validated_data
        )
        
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data.copy()
        categoria_id = data.pop('categoria_id', None)
        
        if categoria_id:
            data['categoria'] = Categoria.objects.get(id=categoria_id)
        
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        
        imagenes = Multimedio.objects.filter(producto=instance)
        
        for img in imagenes:
            if img.archivo_url and 'cloudinary.com' in img.archivo_url:
                try:
                    parts = img.archivo_url.split('/upload/')
                    if len(parts) > 1:
                        public_id = parts[1].split('.')[0]
                        CloudinaryService.delete_image(public_id)
                except Exception as e:
                    print(f"Error deleting from Cloudinary: {e}")
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
