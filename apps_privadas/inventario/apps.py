from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps_privadas.inventario'

    def ready(self):
        import apps_privadas.inventario.signals
