import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventario', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Promocion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=150)),
                ('descripcion', models.TextField(blank=True, default='')),
                ('tipo_descuento', models.CharField(choices=[('porcentaje', 'Porcentaje'), ('monto_fijo', 'Monto fijo')], max_length=20)),
                ('valor_descuento', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('estado', models.CharField(choices=[('borrador', 'Borrador'), ('publicada', 'Publicada'), ('finalizada', 'Finalizada'), ('cancelada', 'Cancelada')], default='borrador', max_length=20)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('fecha_publicacion', models.DateTimeField(blank=True, null=True)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promociones_creadas', to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promociones', to='inventario.producto')),
            ],
            options={
                'verbose_name': 'Promocion',
                'verbose_name_plural': 'Promociones',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.URLField(max_length=1000, unique=True)),
                ('p256dh', models.CharField(max_length=255)),
                ('auth', models.CharField(max_length=255)),
                ('user_agent', models.TextField(blank=True, default='')),
                ('activa', models.BooleanField(default=True)),
                ('ultimo_envio', models.DateTimeField(blank=True, null=True)),
                ('ultimo_error', models.TextField(blank=True, default='')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('ultima_promocion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notificaciones_enviadas', to='notificaciones.promocion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones_push', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificacion push',
                'verbose_name_plural': 'Notificaciones push',
                'ordering': ['-fecha_actualizacion'],
            },
        ),
    ]
