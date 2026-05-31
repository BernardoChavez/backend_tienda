from django.core.management.base import BaseCommand
from django.db.models import Q
from django_tenants.utils import tenant_context

from apps_publicas.empresas.models import Empresa
from apps_privadas.inventario.models import Producto
from apps_privadas.inventario.services.embedding_client import obtener_embedding


class Command(BaseCommand):
    help = 'Procesa embeddings pendientes de productos de todos los tenants'

    def handle(self, *args, **options):
        tenants = Empresa.objects.exclude(schema_name='public')
        self.stdout.write(f"Tenants encontrados: {tenants.count()}")

        for tenant in tenants:
            with tenant_context(tenant):
                self.stdout.write(f"\n--- Tenant: {tenant.schema_name} ---")

                productos = Producto.objects.filter(
                    Q(embedding_sync_status='pending') | Q(embedding__isnull=True, embedding_sync_status='')
                ).select_related('categoria', 'marca')

                total = productos.count()
                if total == 0:
                    self.stdout.write("  Sin productos pendientes")
                    continue

                self.stdout.write(f"  Productos por procesar: {total}")

                for i, p in enumerate(productos, 1):
                    self.stdout.write(f"  [{i}/{total}] {p.nombre}...", ending=' ')
                    try:
                        vector = obtener_embedding(
                            p.nombre,
                            p.descripcion,
                            p.categoria.nombre,
                            p.marca.nombre,
                        )
                        Producto.objects.filter(id=p.id).update(
                            embedding=vector,
                            embedding_sync_status='completed'
                        )
                        self.stdout.write(self.style.SUCCESS("OK"))
                    except Exception as e:
                        Producto.objects.filter(id=p.id).update(
                            embedding_sync_status='failed'
                        )
                        self.stdout.write(self.style.ERROR(f"FALLÓ - {e}"))

        self.stdout.write(self.style.SUCCESS("\nProcesamiento finalizado"))
