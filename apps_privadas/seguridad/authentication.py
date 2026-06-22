from django.db import connection
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class TenantJWTAuthentication(JWTAuthentication):
    """Valida que el JWT pertenezca al tenant/schema de la request actual."""

    def get_user(self, validated_token):
        token_schema = validated_token.get('tenant_schema')
        current_schema = getattr(connection, 'schema_name', None)

        if token_schema and current_schema and token_schema != current_schema:
            raise AuthenticationFailed(
                'El token no pertenece a esta empresa.',
                code='wrong_tenant',
            )

        return super().get_user(validated_token)
