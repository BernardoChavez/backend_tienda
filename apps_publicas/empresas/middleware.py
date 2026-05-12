from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model


class TenantMiddleware(TenantMainMiddleware):
    # ESTO ES LO QUE FALTA: Atrapamos la request aquí
    def process_request(self, request):
        self.request = request
        return super().process_request(request)

    def get_tenant(self, domain_model, hostname):
        # Ahora self.request sí existe y el print funcionará
        tenant_header = self.request.META.get('HTTP_X_TENANT')
        print(f"DEBUG: Encabezado recibido -> {tenant_header}")

        if tenant_header:
            TenantModel = get_tenant_model()
            try:
                return TenantModel.objects.get(schema_name=tenant_header)
            except TenantModel.DoesNotExist:
                print(f"ERROR: El tenant {tenant_header} no existe")
                pass
        return super().get_tenant(domain_model, hostname)