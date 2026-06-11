import os
import subprocess
import tempfile
from django.conf import settings
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class TenantBackupDownloadView(APIView):
    """
    Genera y descarga un backup del esquema PostgreSQL del tenant actual.

    Requiere autenticación JWT. Usa pg_dump nativo para exportar
    únicamente el esquema del tenant (no el esquema public ni otros tenants).

    Endpoint: GET /api/seguridad/backup/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Esquema del tenant activo, ej: "empresa_abc"
        schema_name = request.tenant.schema_name

        print(f"=== BACKUP iniciado para schema: {schema_name} ===")

        db = settings.DATABASES['default']
        db_name = db['NAME']
        db_user = db['USER']
        db_host = db['HOST']
        db_port = str(db['PORT'])
        db_password = db['PASSWORD']

        print(f"=== DB: {db_host}:{db_port}/{db_name} ===")

        # Archivo temporal donde pg_dump escribirá el backup
        tmp_file = tempfile.NamedTemporaryFile(
            suffix='.dump',
            prefix=f'backup_{schema_name}_',
            delete=False,
        )
        tmp_path = tmp_file.name
        tmp_file.close()

        env = os.environ.copy()
        # pg_dump y pg_restore leen la contraseña desde esta variable de entorno
        # para evitar el prompt interactivo de contraseña
        env['PGPASSWORD'] = db_password

        try:
            result = subprocess.run(
                [
                    'pg_dump',
                    '--host', db_host,           # Servidor PostgreSQL (Supabase host)
                    '--port', db_port,            # Puerto, normalmente 5432
                    '--username', db_user,        # Usuario con acceso al schema
                    '--dbname', db_name,          # Base de datos destino
                    '--schema', schema_name,      # -n: exporta SOLO este esquema
                    '--format', 'c',              # -F c: formato custom comprimido (requerido para pg_restore)
                    '--no-owner',                 # Omite sentencias OWNER para portabilidad
                    '--no-acl',                   # Omite sentencias GRANT/REVOKE
                    '--file', tmp_path,           # Archivo de salida
                ],
                env=env,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"PG_DUMP ERROR: {result.stderr}")
                print(f"PG_DUMP STDOUT: {result.stdout}")
                return Response(
                    {'error': 'pg_dump falló', 'detalle': result.stderr},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            filename = f'backup_{schema_name}.dump'
            file_handle = open(tmp_path, 'rb')

            response = FileResponse(
                file_handle,
                as_attachment=True,
                filename=filename,
                content_type='application/octet-stream',
            )
            # Django cierra el file_handle al terminar de enviar la respuesta;
            # el archivo temporal se elimina en el bloque finally
            response._resource_closers.append(lambda: _cleanup(tmp_path))
            return response

        except FileNotFoundError:
            return Response(
                {'error': 'pg_dump no encontrado. Instale postgresql-client en el servidor.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            _cleanup(tmp_path)
            return Response(
                {'error': 'Error inesperado al generar el backup', 'detalle': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            # Eliminar la contraseña del entorno de proceso en curso
            env.pop('PGPASSWORD', None)


def _cleanup(path: str) -> None:
    """Elimina el archivo temporal si aún existe."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass