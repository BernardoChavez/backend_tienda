from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model


class TenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        # Primero intenta por header X-Tenant (móvil/Flutter)
        request = self.request if hasattr(self, 'request') else None
        if request:
            tenant_header = request.META.get('HTTP_X_TENANT')
            if tenant_header:
                TenantModel = get_tenant_model()
                try:
                    return TenantModel.objects.get(schema_name=tenant_header)
                except TenantModel.DoesNotExist:
                    pass

        # Si no hay header, usa subdominio (web)
        return super().get_tenant(domain_model, hostname)