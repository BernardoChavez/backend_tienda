from apps_privadas.inventario.models.producto import Producto
from apps_privadas.inventario.models.resena import Resena


class ResenaService:

    @staticmethod
    def _verificar_compra(usuario, producto_id):
        from apps_privadas.venta.models.detalle_venta import DetalleVenta
        return DetalleVenta.objects.filter(
            venta__usuario=usuario,
            venta__estado='completado',
            variante_producto__producto_id=producto_id,
        ).exists()

    @staticmethod
    def crear_resena(usuario, producto_id, calificacion, comentario=''):
        if not ResenaService._verificar_compra(usuario, producto_id):
            return {'success': False, 'error': 'Solo puedes reseñar productos que hayas comprado.'}

        if Resena.objects.filter(usuario=usuario, producto_id=producto_id).exists():
            return {'success': False, 'error': 'Ya tienes una reseña para este producto.'}

        producto = Producto.objects.get(id=producto_id)
        resena = Resena.objects.create(
            usuario=usuario,
            producto=producto,
            calificacion=calificacion,
            comentario=comentario,
        )
        return {'success': True, 'resena': resena}

    @staticmethod
    def actualizar_resena(resena, usuario, calificacion=None, comentario=None):
        if resena.usuario != usuario:
            return {'success': False, 'error': 'No puedes editar la reseña de otro usuario.'}

        if calificacion is not None:
            resena.calificacion = calificacion
        if comentario is not None:
            resena.comentario = comentario
        resena.save()
        return {'success': True, 'resena': resena}

    @staticmethod
    def eliminar_resena(resena, usuario):
        if resena.usuario != usuario:
            return {'success': False, 'error': 'No puedes eliminar la reseña de otro usuario.'}

        resena.delete()
        return {'success': True}