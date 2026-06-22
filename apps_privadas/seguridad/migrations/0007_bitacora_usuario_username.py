from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seguridad', '0006_bitacora_por_tenant'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitacoraauditoria',
            name='usuario_username',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
