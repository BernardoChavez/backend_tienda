from apps_privadas.venta.models import Venta, DetalleVenta
from apps_privadas.compras.models import Compra, DetalleCompra
from apps_privadas.inventario.models import Producto, VarianteProducto, Categoria, Marca
from apps_privadas.seguridad.models import Usuario

REPORT_CONFIG = {
    "modelos": {
        "venta": Venta,
        "detalle_venta": DetalleVenta,
        "compra": Compra,
        "detalle_compra": DetalleCompra,
        "producto": Producto,
        "variante": VarianteProducto,
        "categoria": Categoria,
        "marca": Marca,
        "cliente": Usuario,
    },

    "mapa_campos": {
        "venta": {
            "id": "id",
            "tipo": "tipo",
            "estado": "estado",
            "fecha": "fecha",
            "precio_total": "precio_total",
            "usuario_id": "usuario_id",
            "cliente_nombre": "usuario__nombre",
            "cliente_apellido": "usuario__apellido",
            "cliente_username": "usuario__username",
        },

        "detalle_venta": {
            "id": "id",
            "cantidad": "cantidad",
            "precio_subtotal": "precio_subtotal",
            "precio_unitario": "precio_unitario",
            "venta_id": "venta_id",
            "venta_fecha": "venta__fecha",
            "venta_estado": "venta__estado",
            "venta_tipo": "venta__tipo",
            "variante_id": "variante_producto_id",
            "variante_sku": "variante_producto__sku",
            "producto_id": "variante_producto__producto__id",
            "producto_nombre": "variante_producto__producto__nombre",
            "categoria_id": "variante_producto__producto__categoria_id",
            "categoria_nombre": "variante_producto__producto__categoria__nombre",
            "marca_id": "variante_producto__producto__marca_id",
            "marca_nombre": "variante_producto__producto__marca__nombre",
        },

        "compra": {
            "id": "id",
            "fecha": "fecha",
            "total": "total",
            "proveedor_id": "proveedor_id",
            "proveedor_nombre": "proveedor__nombre",
        },

        "detalle_compra": {
            "id": "id",
            "cantidad": "cantidad",
            "costo_subtotal": "costo_subtotal",
            "costo_unitario": "costo_unitario",
            "compra_id": "compra_id",
            "compra_fecha": "compra__fecha",
            "variante_id": "variante_producto_id",
            "variante_sku": "variante_producto__sku",
            "producto_id": "variante_producto__producto__id",
            "producto_nombre": "variante_producto__producto__nombre",
            "categoria_nombre": "variante_producto__producto__categoria__nombre",
        },

        "producto": {
            "id": "id",
            "nombre": "nombre",
            "descripcion": "descripcion",
            "activo": "activo",
            "categoria_id": "categoria_id",
            "categoria_nombre": "categoria__nombre",
            "marca_id": "marca_id",
            "marca_nombre": "marca__nombre",
        },

        "variante": {
            "id": "id",
            "sku": "sku",
            "precio": "precio",
            "cantidad": "cantidad",
            "costo_ponderado": "costo_ponderado",
            "limite_cantidad": "limite_cantidad",
            "producto_id": "producto_id",
            "producto_nombre": "producto__nombre",
        },

        "categoria": {
            "id": "id",
            "nombre": "nombre",
        },

        "marca": {
            "id": "id",
            "nombre": "nombre",
        },

        "cliente": {
            "id": "id",
            "username": "username",
            "nombre": "nombre",
            "apellido": "apellido",
            "email": "email",
            "fecha_registro": "date_joined",
        },
    }
}