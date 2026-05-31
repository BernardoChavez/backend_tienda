from rest_framework import viewsets, status
from datetime import datetime

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps_privadas.carrito.models import Carrito, DetalleCarrito
from apps_privadas.carrito.serializers import CarritoSerializer, DetalleCarritoSerializer
from apps_privadas.inventario.models import VarianteProducto
from django.http import FileResponse
from apps_privadas.carrito.utils import generar_pdf_cotizacion
from django.db import connection


class CarritoViewSet(viewsets.ModelViewSet):
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve su propio carrito
        return Carrito.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['get', 'post'])
    def mi_carrito(self, request):
        """Obtener o crear el carrito del usuario actual"""
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def agregar_producto(self, request):
        """Agregar un producto al carrito o aumentar cantidad"""
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        variante_id = request.data.get('variante_id')
        cantidad = int(request.data.get('cantidad', 1))

        variante = get_object_or_404(VarianteProducto, id=variante_id)
        
        # Validar stock
        if variante.cantidad < cantidad:
            return Response(
                {"error": f"Stock insuficiente. Disponible: {variante.cantidad}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        detalle, created = DetalleCarrito.objects.get_or_create(
            carrito=carrito,
            variante_producto=variante,
            defaults={'cantidad': cantidad}
        )

        if not created:
            detalle.cantidad += cantidad
            if detalle.cantidad > variante.cantidad:
                 return Response(
                    {"error": "No puedes agregar más de lo disponible en stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            detalle.save()

        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def quitar_producto(self, request):
        """Quitar un producto del carrito"""
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        variante_id = request.data.get('variante_id')
        
        detalle = get_object_or_404(DetalleCarrito, carrito=carrito, variante_producto_id=variante_id)
        detalle.delete()

        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def actualizar_cantidad(self, request):
        """Actualizar la cantidad exacta de un producto"""
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        variante_id = request.data.get('variante_id')
        cantidad = int(request.data.get('cantidad', 1))

        if cantidad <= 0:
            return self.quitar_producto(request)

        variante = get_object_or_404(VarianteProducto, id=variante_id)
        if variante.cantidad < cantidad:
            return Response(
                {"error": "Stock insuficiente"},
                status=status.HTTP_400_BAD_REQUEST
            )

        detalle = get_object_or_404(DetalleCarrito, carrito=carrito, variante_producto=variante)
        detalle.cantidad = cantidad
        detalle.save()

        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def vaciar(self, request):
        """Eliminar todos los productos del carrito"""
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        carrito.detalles.all().delete()
        
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'])
    def descargar_pdf(self, request):
        """Generar y descargar cotización en PDF"""
        carrito = get_object_or_404(Carrito, usuario=request.user)
        
        # Validar que tenga items
        if not carrito.detalles.exists():
            return Response(
                {"error": "El carrito está vacío"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Obtener datos de la empresa (tenant actual)
        empresa = connection.tenant
        
        # Obtener datos de configuración personalizados enviados desde el frontend (si los hay)
        custom_config = {}
        if request.method == 'POST':
            custom_config = request.data
        else:
            custom_config = request.query_params.dict()
            
        pdf_buffer = generar_pdf_cotizacion(carrito, empresa, custom_config)
        
        nombre_empresa = custom_config.get('nombre') or empresa.nombre
        
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            content_type='application/pdf',
            filename=f"Cotizacion_{nombre_empresa}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

