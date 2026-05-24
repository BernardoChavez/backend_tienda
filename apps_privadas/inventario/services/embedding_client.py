import logging

import requests
from django.conf import settings

from apps_privadas.inventario.models import Producto

logger = logging.getLogger(__name__)


def obtener_embedding(nombre, descripcion, categoria, marca):
    url = settings.EMBEDDING_SERVICE_URL
    if not url:
        raise ValueError("EMBEDDING_SERVICE_URL no está configurado")

    texto = f"Producto: {nombre}\nMarca: {marca}\nCategoría: {categoria}\nDescripción: {descripcion}"

    resp = requests.post(
        f"{url}/api/vectorize",
        json={"text": texto},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def generar_embedding_sync(producto):
    if not settings.EMBEDDING_SERVICE_URL:
        logger.warning("EMBEDDING_SERVICE_URL no está configurado - saltando embedding")
        return
    try:
        vector = obtener_embedding(
            producto.nombre,
            producto.descripcion,
            producto.categoria.nombre,
            producto.marca.nombre,
        )
        Producto.objects.filter(id=producto.id).update(
            embedding=vector,
            embedding_sync_status='completed'
        )
        logger.info("Embedding generado correctamente para producto %s (ID %s)", producto.nombre, producto.id)
    except Exception as e:
        logger.exception("Error al generar embedding para producto %s (ID %s): %s", producto.nombre, producto.id, e)
        Producto.objects.filter(id=producto.id).update(
            embedding_sync_status='failed'
        )
