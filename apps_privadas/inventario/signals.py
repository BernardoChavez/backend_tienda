import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps_privadas.inventario.models import Producto
from apps_privadas.inventario.services.embedding_client import obtener_embedding


@receiver(post_save, sender=Producto)
def generar_embedding(sender, instance, **kwargs):
    if instance.embedding_sync_status != 'pending':
        return

    Producto.objects.filter(id=instance.id).update(
        embedding_sync_status='processing'
    )

    def _process(pid, nombre, descripcion, cat, marca):
        try:
            vector = obtener_embedding(nombre, descripcion, cat, marca)
            Producto.objects.filter(id=pid).update(
                embedding=vector,
                embedding_sync_status='completed'
            )
        except Exception:
            Producto.objects.filter(id=pid).update(
                embedding_sync_status='failed'
            )

    t = threading.Thread(
        target=_process,
        args=(
            instance.id,
            instance.nombre,
            instance.descripcion,
            instance.categoria.nombre,
            instance.marca.nombre,
        )
    )
    t.start()
