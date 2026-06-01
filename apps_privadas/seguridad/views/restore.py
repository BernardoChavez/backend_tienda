import os
import subprocess
import tempfile

from django.conf import settings
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class TenantRestoreView(APIView):
    """
    Restaura el esquema del tenant actual desde un archivo .dump generado por pg_dump.

    Acepta un archivo multipart con clave 'backup_file'.
    ADVERTENCIA: La opción --clean elimina y recrea los objetos del esquema antes
    de restaurar. Esta operación NO se puede deshacer.

    Endpoint: POST /api/seguridad/restore/
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        backup_file = request.FILES.get('backup_file')
        if not backup_file:
            return Response(
                {'error': "Se requiere el campo 'backup_file' con el archivo .dump"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schema_name = request.tenant.schema_name

        db = settings.DATABASES['default']
        db_name = db['NAME']
        db_user = db['USER']
        db_host = db['HOST']
        db_port = str(db['PORT'])
        db_password = db['PASSWORD']

        # Guardar el archivo subido en un temporal en disco para pasárselo a pg_restore
        tmp_file = tempfile.NamedTemporaryFile(
            suffix='.dump',
            prefix=f'restore_{schema_name}_',
            delete=False,
        )
        tmp_path = tmp_file.name

        try:
            for chunk in backup_file.chunks():
                tmp_file.write(chunk)
            tmp_file.flush()
            tmp_file.close()
        except Exception as exc:
            tmp_file.close()
            _cleanup(tmp_path)
            return Response(
                {'error': 'No se pudo guardar el archivo temporal', 'detalle': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        env = os.environ.copy()
        # pg_restore lee la contraseña desde PGPASSWORD para evitar el prompt interactivo
        env['PGPASSWORD'] = db_password

        try:
            result = subprocess.run(
                [
                    'pg_restore',
                    '--host', db_host,            # Servidor PostgreSQL (Supabase host)
                    '--port', db_port,             # Puerto, normalmente 5432
                    '--username', db_user,         # Usuario con permisos de escritura
                    '--dbname', db_name,           # Base de datos destino
                    '--schema', schema_name,       # -n: restaura SOLO en este esquema
                    '--clean',                     # -c: DROP + CREATE antes de restaurar (requiere que los objetos ya existan)
                    '--if-exists',                 # Complemento de --clean: no falla si el objeto no existe al hacer DROP
                    '--single-transaction',        # -1: todo en una transacción; si algo falla se hace rollback completo
                    '--no-owner',                  # No restaura OWNER (el usuario actual asume la propiedad)
                    '--no-acl',                    # No restaura GRANT/REVOKE
                    tmp_path,                      # Archivo .dump a restaurar (último argumento posicional)
                ],
                env=env,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return Response(
                    {'error': 'pg_restore falló', 'detalle': result.stderr},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {'mensaje': f"Restauración del esquema '{schema_name}' completada exitosamente."},
                status=status.HTTP_200_OK,
            )

        except FileNotFoundError:
            return Response(
                {'error': 'pg_restore no encontrado. Instale postgresql-client en el servidor.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            return Response(
                {'error': 'Error inesperado durante la restauración', 'detalle': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            env.pop('PGPASSWORD', None)
            _cleanup(tmp_path)


def _cleanup(path: str) -> None:
    """Elimina el archivo temporal si aún existe."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass