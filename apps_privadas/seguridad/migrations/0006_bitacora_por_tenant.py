from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seguridad', '0005_bitacora_request_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
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
                            metodo VARCHAR(10),
                            ruta VARCHAR(255),
                            ip_cliente INET,
                            estado_http INTEGER
                        );
                    """,
                    reverse_sql="DROP TABLE IF EXISTS bitacora;",
                ),
            ],
            state_operations=[
                migrations.AlterModelTable(
                    name='bitacoraauditoria',
                    table='bitacora',
                ),
                migrations.AlterModelOptions(
                    name='bitacoraauditoria',
                    options={
                        'ordering': ['-fecha', '-hora', '-id_bitacora'],
                        'verbose_name': 'Bitacora de auditoria',
                        'verbose_name_plural': 'Bitacoras de auditoria',
                    },
                ),
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
            ],
        ),
    ]
