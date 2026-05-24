from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0004_producto_embedding_producto_embedding_sync_status'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_producto_embedding "
            "ON inventario_producto USING hnsw (embedding vector_cosine_ops)",
            reverse_sql="DROP INDEX IF EXISTS idx_producto_embedding"
        ),
    ]
