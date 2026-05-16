from django.contrib.auth.models import Group

from apps_privadas.seguridad.models.usuario import Usuario


class ClienteService:
    """Servicio para registro de clientes"""

    @staticmethod
    def registrar_cliente(username, password, nombre, apellido, fecha_nacimiento):
        """
        Registra un nuevo cliente.
        El grupo sera automaticamente "Cliente".

        Args:
            username (str): Nombre de usuario unico
            password (str): Contrasena
            nombre (str): Nombre obligatorio
            apellido (str): Apellido obligatorio
            fecha_nacimiento (str): Fecha nacimiento obligatoria (YYYY-MM-DD)

        Returns:
            dict: {
                'success': bool,
                'cliente_id': int,
                'username': str,
                'nombre_completo': str,
                'mensaje': str
            }
        """
        try:
            # Validar que los campos obligatorios existan
            if not all([nombre, apellido, fecha_nacimiento]):
                return {
                    'success': False,
                    'error': 'Nombre, apellido y fecha de nacimiento son obligatorios'
                }

            # Verificar que el username sea unico (solo en usuarios activos)
            if Usuario.objects.filter(username=username, is_active=True).exists():
                return {
                    'success': False,
                    'error': f'El usuario {username} ya existe'
                }

            # Obtener o crear el grupo "Cliente"
            grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')

            # Crear el cliente (usuario)
            cliente = Usuario.objects.create_user(
                username=username,
                password=password,
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento
            )

            # Asignar al grupo Cliente
            cliente.groups.add(grupo_cliente)

            print(f"✓ Cliente registrado: {cliente.username}")
            print(f"  Nombre: {cliente.nombre_completo}")
            print(f"  Grupo: {grupo_cliente.name}")

            return {
                'success': True,
                'cliente_id': cliente.id,
                'username': cliente.username,
                'nombre_completo': cliente.nombre_completo,
                'mensaje': f'Cliente {username} registrado exitosamente'
            }

        except Exception as e:
            print(f"❌ Error registrando cliente: {str(e)}")
            return {
                'success': False,
                'error': f'Error registrando cliente: {str(e)}'
            }

