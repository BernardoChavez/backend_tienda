from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seguridad', '0005_bitacora_request_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Estos 4 campos fueron creados via RunSQL en 0005 pero nunca
                # registrados en el estado de Django con AddField.
                migrations.AddField(
                    model_name='bitacoraauditoria',
                    name='metodo',
                    field=models.CharField(blank=True, max_length=10, null=True),
                ),
                migrations.AddField(
                    model_name='bitacoraauditoria',
                    name='ruta',
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                migrations.AddField(
                    model_name='bitacoraauditoria',
                    name='ip_cliente',
                    field=models.GenericIPAddressField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='bitacoraauditoria',
                    name='estado_http',
                    field=models.IntegerField(blank=True, null=True),
                ),
                # Cambiar a managed=True y tabla por tenant
                migrations.AlterModelOptions(
                    name='bitacoraauditoria',
                    options={
                        'managed': True,
                        'ordering': ['-fecha', '-hora', '-id_bitacora'],
                        'verbose_name': 'Bitacora de auditoria',
                        'verbose_name_plural': 'Bitacoras de auditoria',
                    },
                ),
                migrations.AlterModelTable(
                    name='bitacoraauditoria',
                    table='bitacora',
                ),
                migrations.AddField(
                    model_name='bitacoraauditoria',
                    name='usuario_username',
                    field=models.CharField(blank=True, max_length=150, null=True),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        CREATE TABLE IF NOT EXISTS bitacora (
                            id_bitacora BIGSERIAL PRIMARY KEY,
                            fecha DATE NOT NULL,
                            hora TIME NOT NULL,
                            entidad VARCHAR(100) NOT NULL,
                            detalles VARCHAR(500) NOT NULL,
                            accion VARCHAR(100) NOT NULL,
                            usuarios_id BIGINT NOT NULL,
                            usuario_username VARCHAR(150),
                            metodo VARCHAR(10),
                            ruta VARCHAR(255),
                            ip_cliente INET,
                            estado_http INTEGER
                        );
                    """,
                    reverse_sql="DROP TABLE IF EXISTS bitacora;",
                ),
            ],
        ),
    ]