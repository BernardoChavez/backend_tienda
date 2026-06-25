from django.apps import AppConfig


class SeguridadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps_privadas.seguridad'

    def ready(self):
        from apps_privadas.seguridad.models import usuario  # noqa: F401
        from apps_privadas.seguridad.models import codigo_recuperacion  # noqa: F401
        from apps_privadas.seguridad.models import bitacora_auditoria  # noqa: F401
        from apps_privadas.seguridad import signals  # noqa: F401
