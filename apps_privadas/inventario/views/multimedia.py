from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.conf import settings

from apps_privadas.inventario.models import Multimedio, Producto
from apps_privadas.inventario.serializers import (
    MultimedioSerializer,
    CrearMultimedioSerializer,
    ActualizarMultimedioSerializer,
    MultimedioConArchivoSerializer
)
from apps_privadas.inventario.cloudinary_service import CloudinaryService


class MultimedioViewSet(viewsets.ModelViewSet):
    queryset = Multimedio.objects.select_related('producto').all()
    serializer_class = MultimedioSerializer
    crear_serializer_class = CrearMultimedioSerializer
    actualizar_serializer_class = ActualizarMultimedioSerializer
    permission_classes = [IsAuthenticated]
    model = Multimedio
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'create':
            if 'archivo' in self.request.data:
                return MultimedioConArchivoSerializer
            return self.crear_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.actualizar_serializer_class
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        print("ENTRO ACA")
        if 'archivo' in request.data:
            return self.crear_con_archivo(request, *args, **kwargs)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        producto_id = data.pop('producto_id')

        instance = self.model.objects.create(
            producto_id=producto_id,
            **data
        )

        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def crear_con_archivo(self, request, *args, **kwargs):
        """Crea multimedia subiendo archivo a Cloudinary"""
        print("SI ENTRO AL CREAR")
        serializer = MultimedioConArchivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        archivo = data.pop('archivo')
        producto_id = data.pop('producto_id')
        
        try:
            result = CloudinaryService.upload_image(
                archivo,
                folder='tienda/productos'
            )
            
            nombre = archivo.name.split('.')[0] if archivo.name else 'imagen'
            
            instance = self.model.objects.create(
                producto_id=producto_id,
                nombre=nombre,
                archivo_url=result['secure_url'],
                tipo=data.get('tipo', 'imagen'),
                es_principal=data.get('es_principal', False),
                orden=data.get('orden', 0)
            )

            return Response(
                self.serializer_class(instance).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error al subir archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        
        if 'archivo' in request.data:
            return self.actualizar_con_archivo(request, instance, *args, **kwargs)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        producto_id = data.pop('producto_id', None)

        if producto_id:
            data['producto_id'] = producto_id

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()

        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def actualizar_con_archivo(self, request, instance, *args, **kwargs):
        """Actualiza multimedia subiendo nuevo archivo a Cloudinary"""
        archivo = request.FILES.get('archivo')
        print("SI ENTRO A ACTUALIZAR")
        if not archivo:
            return Response(
                {'error': 'No se proporcionó archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = CloudinaryService.upload_image(
                archivo,
                folder='tienda/productos'
            )
            
            instance.nombre = archivo.name.split('.')[0] if archivo.name else instance.nombre
            instance.archivo_url = result['secure_url']
            instance.save()

            return Response(
                self.serializer_class(instance).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Error al subir archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        print("=== ENTRO AL DELETE de multimedia ===")
        instance = self.get_object()
        archivo_url = getattr(instance, 'archivo_url', None)
        public_id = None
        print(f"=== instance: {instance.id}, archivo_url: {archivo_url} ===")
        
        if archivo_url and 'cloudinary.com' in archivo_url:
            try:
                path = archivo_url.split('/upload/')[1]
                if path.startswith('v'):
                    path = '/'.join(path.split('/')[1:])
                public_id = path.rsplit('.', 1)[0]
                print(f"=== public_id extracted: {public_id} ===")
            except Exception as e:
                print(f"No se pudo extraer public_id: {e}")

        instance.delete()
        print("=== Deleted from DB ===")

        if public_id:
            print(f"=== Deleting from Cloudinary: {public_id} ===")
            try:
                resultado = CloudinaryService.delete_image(public_id)
                print(f"=== Cloudinary result: {resultado} ===")
            except Exception as e:
                print(f"ERROR deleting from Cloudinary: {e}")

        return Response(status=status.HTTP_204_NO_CONTENT)
