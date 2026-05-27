from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seguridad', '0004_alter_codigorecuperacion_options'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE SCHEMA IF NOT EXISTS auditoria;
                CREATE TABLE IF NOT EXISTS auditoria.bitacora (
                    id_bitacora BIGSERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    hora TIME NOT NULL,
                    entidad VARCHAR(100) NOT NULL,
                    detalles VARCHAR(500) NOT NULL,
                    accion VARCHAR(100) NOT NULL,
                    usuarios_id BIGINT NOT NULL
                );
                ALTER TABLE auditoria.bitacora
                    ADD COLUMN IF NOT EXISTS metodo VARCHAR(10),
                    ADD COLUMN IF NOT EXISTS ruta VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS ip_cliente INET,
                    ADD COLUMN IF NOT EXISTS estado_http INTEGER;
            """,
            reverse_sql="""
                ALTER TABLE auditoria.bitacora
                    DROP COLUMN IF EXISTS estado_http,
                    DROP COLUMN IF EXISTS ip_cliente,
                    DROP COLUMN IF EXISTS ruta,
                    DROP COLUMN IF EXISTS metodo;
            """,
        ),
    ]
