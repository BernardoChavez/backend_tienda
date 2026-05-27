from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0004_producto_embedding_producto_embedding_sync_status'),
    ]

    operations = [
        migrations.RunSQL(
            "SELECT 1",
            reverse_sql="SELECT 1"
        ),
    ]
