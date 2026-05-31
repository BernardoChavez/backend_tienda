from django.contrib.auth.models import Group

from apps_privadas.seguridad.models.usuario import Usuario


class UsuarioService:
    """Servicio para operaciones CRUD de usuarios"""

    @staticmethod
    def crear_usuario(username, password, grupo_id, email=None):
        """
        Crea un nuevo usuario.

        Args:
            username (str): Nombre de usuario unico
            password (str): Contrasena
            grupo_id (int): ID del grupo/rol obligatorio

        Returns:
            dict: {
                'success': bool,
                'usuario_id': int,
                'username': str,
                'grupo': str,
                'mensaje': str
            }
        """
        try:
            # Validar que el grupo exista
            try:
                grupo = Group.objects.get(id=grupo_id)
            except Group.DoesNotExist:
                return {
                    'success': False,
                    'error': f'El grupo con ID {grupo_id} no existe'
                }

            # Verificar que el username sea unico (solo en usuarios activos)
            if Usuario.objects.filter(username=username, is_active=True).exists():
                return {
                    'success': False,
                    'error': f'El usuario {username} ya existe'
                }

            # Crear el usuario
            usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                email=email or ''
            )

            # Asignar al grupo
            usuario.groups.add(grupo)

            print(f"OK Usuario creado: {usuario.username}")
            print(f"  Grupo: {grupo.name}")

            return {
                'success': True,
                'usuario_id': usuario.id,
                'username': usuario.username,
                'grupo': grupo.name,
                'mensaje': f'Usuario {username} creado exitosamente'
            }

        except Exception as e:
            print(f"ERROR creando usuario: {str(e)}")
            return {
                'success': False,
                'error': f'Error creando usuario: {str(e)}'
            }

    @staticmethod
    def actualizar_usuario(usuario_id, password=None, grupo_id=None, email=None):
        """
        Actualiza un usuario.

        Args:
            usuario_id (int): ID del usuario
            password (str, optional): Nueva contrasena
            grupo_id (int, optional): ID del nuevo grupo

        Returns:
            dict: {
                'success': bool,
                'usuario_id': int,
                'username': str,
                'mensaje': str
            }
        """
        try:
            # Obtener el usuario
            try:
                usuario = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                return {
                    'success': False,
                    'error': f'El usuario con ID {usuario_id} no existe'
                }

            # Actualizar email si se proporciona
            if email is not None:
                usuario.email = email

            # Actualizar contrasena si se proporciona
            if password:
                usuario.set_password(password)

            # Actualizar grupo si se proporciona
            if grupo_id:
                try:
                    grupo = Group.objects.get(id=grupo_id)
                    usuario.groups.clear()
                    usuario.groups.add(grupo)
                except Group.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'El grupo con ID {grupo_id} no existe'
                    }

            usuario.save()

            print(f"OK Usuario actualizado: {usuario.username}")

            return {
                'success': True,
                'usuario_id': usuario.id,
                'username': usuario.username,
                'mensaje': f'Usuario {usuario.username} actualizado'
            }

        except Exception as e:
            print(f"ERROR actualizando usuario: {str(e)}")
            return {
                'success': False,
                'error': f'Error actualizando usuario: {str(e)}'
            }

    @staticmethod
    def obtener_usuario(usuario_id):
        """Obtiene un usuario por ID"""
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            grupos = list(usuario.groups.values_list('name', flat=True))

            return {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'fecha_nacimiento': usuario.fecha_nacimiento,
                'grupos': grupos,
                'is_active': usuario.is_active,
                'is_superuser': usuario.is_superuser,
                'date_joined': usuario.date_joined
            }
        except Usuario.DoesNotExist:
            return None

    @staticmethod
    def listar_usuarios():
        """Lista todos los usuarios activos"""
        usuarios = Usuario.objects.filter(is_active=True)
        resultado = []

        for usuario in usuarios:
            grupos = list(usuario.groups.values_list('name', flat=True))
            resultado.append({
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'grupos': grupos,
                'is_superuser': usuario.is_superuser,
                'date_joined': usuario.date_joined
            })

        return resultado

    @staticmethod
    def eliminar_usuario(usuario_id):
        """Desactiva un usuario (soft delete)"""
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.is_active = False
            usuario.save()

            print(f"OK Usuario desactivado: {usuario.username}")

            return {
                'success': True,
                'mensaje': f'Usuario {usuario.username} desactivado'
            }
        except Usuario.DoesNotExist:
            return {
                'success': False,
                'error': f'El usuario con ID {usuario_id} no existe'
            }

