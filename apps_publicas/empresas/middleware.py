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
        print(f"DEBUG: Encabezado recibido -> {tenant_header}, Hostname -> {hostname}")

        if tenant_header:
            TenantModel = get_tenant_model()
            try:
                tenant = TenantModel.objects.get(schema_name=tenant_header)
                print(f"DEBUG: Tenant resuelto por cabecera -> {tenant.schema_name}")
                return tenant
            except TenantModel.DoesNotExist:
                print(f"ERROR: El tenant {tenant_header} no existe")
                pass

        # FALLBACK PARA MÓVIL Y TÚNELES EN DESARROLLO:
        # Si el hostname es una IP, localhost o un túnel ngrok, devolvemos el tenant 'tienda_amiga'
        import re
        if (re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname) or 
            hostname == 'localhost' or 
            hostname == '127.0.0.1' or 
            hostname.endswith('ngrok-free.dev') or 
            hostname.endswith('ngrok.io')):
            TenantModel = get_tenant_model()
            try:
                tenant = TenantModel.objects.get(schema_name='tienda_amiga')
                print(f"DEBUG: Tenant resuelto por fallback (ngrok/local) -> {tenant.schema_name}")
                return tenant
            except TenantModel.DoesNotExist:
                pass

        tenant = super().get_tenant(domain_model, hostname)
        print(f"DEBUG: Tenant resuelto por super() -> {tenant.schema_name}")
        return tenant