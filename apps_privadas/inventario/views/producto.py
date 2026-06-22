from apps_privadas.inventario.views.base import BaseViewSet
from rest_framework import status, filters

from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from apps_privadas.inventario.models import Producto, Categoria, Multimedio, Marca
from apps_privadas.inventario.serializers import (
    ProductoSerializer,
    CrearProductoSerializer,
    ActualizarProductoSerializer
)
from apps_privadas.inventario.cloudinary_service import CloudinaryService
from apps_privadas.inventario.services.embedding_client import generar_embedding_sync


def cosine_distance(left, right):
    if not left or not right or len(left) != len(right):
        return None

    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5

    if not left_norm or not right_norm:
        return None

    return 1 - (dot / (left_norm * right_norm))


class ProductoViewSet(BaseViewSet):
    queryset = Producto.objects.select_related('categoria', 'marca').all()
    model = Producto
    serializer_class = ProductoSerializer
    crear_serializer_class = CrearProductoSerializer
    actualizar_serializer_class = ActualizarProductoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion']

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        categoria_id = serializer.validated_data.pop('categoria_id')
        categoria = Categoria.objects.get(id=categoria_id)

        marca_id = serializer.validated_data.pop('marca_id')
        marca = Marca.objects.get(id=marca_id)

        instance = self.model.objects.create(
            categoria=categoria,
            marca=marca,
            **serializer.validated_data
        )

        generar_embedding_sync(instance)
        instance.refresh_from_db()

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
        marca_id = data.pop('marca_id', None)

        if categoria_id:
            data['categoria'] = Categoria.objects.get(id=categoria_id)

        if marca_id:
            data['marca'] = Marca.objects.get(id=marca_id)

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()

        generar_embedding_sync(instance)
        instance.refresh_from_db()

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

    @action(detail=True, methods=['get'])
    def recomendados(self, request, pk=None):
        producto = self.get_object()
        if producto.embedding is None:
            return Response([])

        umbral = float(request.query_params.get('umbral', 0.5))

        candidatos = Producto.objects.select_related('categoria', 'marca') \
            .exclude(id=producto.id) \
            .filter(embedding__isnull=False, activo=True)

        similares = []
        for candidato in candidatos:
            distancia = cosine_distance(producto.embedding, candidato.embedding)
            if distancia is not None and distancia < umbral:
                similares.append((distancia, candidato))

        similares = [producto for _, producto in sorted(similares, key=lambda item: item[0])[:10]]

        return Response(
            ProductoSerializer(similares, many=True).data
        )
