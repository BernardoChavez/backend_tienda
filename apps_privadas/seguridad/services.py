"""
Servicios para gestionar usuarios y clientes.
Contiene toda la lógica de negocio para CRUD de usuarios y registro de clientes.
"""

from django.contrib.auth.models import Group
from apps_privadas.seguridad.models import Usuario


class UsuarioService:
    """Servicio para operaciones CRUD de usuarios"""

    @staticmethod
    def crear_usuario(username, password, grupo_id):
        """
        Crea un nuevo usuario.

        Args:
            username (str): Nombre de usuario único
            password (str): Contraseña
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

            # Verificar que el username sea único (solo en usuarios activos)
            if Usuario.objects.filter(username=username, is_active=True).exists():
                return {
                    'success': False,
                    'error': f'El usuario {username} ya existe'
                }

            # Crear el usuario
            usuario = Usuario.objects.create_user(
                username=username,
                password=password
            )

            # Asignar al grupo
            usuario.groups.add(grupo)

            print(f"✓ Usuario creado: {usuario.username}")
            print(f"  Grupo: {grupo.name}")

            return {
                'success': True,
                'usuario_id': usuario.id,
                'username': usuario.username,
                'grupo': grupo.name,
                'mensaje': f'Usuario {username} creado exitosamente'
            }

        except Exception as e:
            print(f"❌ Error creando usuario: {str(e)}")
            return {
                'success': False,
                'error': f'Error creando usuario: {str(e)}'
            }

    @staticmethod
    def actualizar_usuario(usuario_id, password=None, grupo_id=None):
        """
        Actualiza un usuario.

        Args:
            usuario_id (int): ID del usuario
            password (str, optional): Nueva contraseña
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

            # Actualizar contraseña si se proporciona
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

            print(f"✓ Usuario actualizado: {usuario.username}")

            return {
                'success': True,
                'usuario_id': usuario.id,
                'username': usuario.username,
                'mensaje': f'Usuario {usuario.username} actualizado'
            }

        except Exception as e:
            print(f"❌ Error actualizando usuario: {str(e)}")
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

            print(f"✓ Usuario desactivado: {usuario.username}")

            return {
                'success': True,
                'mensaje': f'Usuario {usuario.username} desactivado'
            }
        except Usuario.DoesNotExist:
            return {
                'success': False,
                'error': f'El usuario con ID {usuario_id} no existe'
            }


class ClienteService:
    """Servicio para registro de clientes"""

    @staticmethod
    def registrar_cliente(username, password, nombre, apellido, fecha_nacimiento):
        """
        Registra un nuevo cliente.
        El grupo será automáticamente "Cliente".

        Args:
            username (str): Nombre de usuario único
            password (str): Contraseña
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

            # Verificar que el username sea único (solo en usuarios activos)
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


# ============================================================================
# SERVICIOS PARA ROLES
# ============================================================================

class RolService:
    """Servicio para operaciones con roles"""

    @staticmethod
    def crear_rol(nombre, permisos_ids=None):
        """Crea un nuevo rol"""
        try:
            from django.contrib.auth.models import Group, Permission

            # Verificar que el rol no exista
            if Group.objects.filter(name=nombre).exists():
                return {
                    'success': False,
                    'error': f'El rol "{nombre}" ya existe'
                }

            # Crear rol
            rol = Group.objects.create(name=nombre)

            # Asignar permisos si se proporcionan
            if permisos_ids:
                permisos = Permission.objects.filter(id__in=permisos_ids)
                rol.permissions.set(permisos)

            print(f"✓ Rol creado: {rol.name}")

            return {
                'success': True,
                'rol_id': rol.id,
                'nombre': rol.name,
                'permisos_count': rol.permissions.count(),
                'mensaje': f'Rol "{nombre}" creado exitosamente'
            }

        except Exception as e:
            print(f"Error creando rol: {str(e)}")
            return {
                'success': False,
                'error': f'Error creando rol: {str(e)}'
            }

    @staticmethod
    def obtener_rol(rol_id):
        """Obtiene información de un rol"""
        from django.contrib.auth.models import Group

        try:
            rol = Group.objects.get(id=rol_id)

            return {
                'id': rol.id,
                'nombre': rol.name,
                'permisos': list(rol.permissions.values('id', 'name', 'codename')),
                'cantidad_usuarios': rol.user_set.count()
            }
        except Group.DoesNotExist:
            return None

    @staticmethod
    def listar_roles():
        """Lista todos los roles"""
        from django.contrib.auth.models import Group

        roles = Group.objects.all().prefetch_related('permissions')

        resultado = []
        for rol in roles:
            resultado.append({
                'id': rol.id,
                'nombre': rol.name,
                'permisos_count': rol.permissions.count(),
                'usuarios_count': rol.user_set.count()
            })

        return resultado

    @staticmethod
    def actualizar_rol(rol_id, nombre=None, permisos_ids=None):
        """Actualiza un rol"""
        from django.contrib.auth.models import Group, Permission

        try:
            rol = Group.objects.get(id=rol_id)

            # Actualizar nombre si se proporciona
            if nombre:
                if Group.objects.filter(name=nombre).exclude(id=rol_id).exists():
                    return {
                        'success': False,
                        'error': f'Ya existe otro rol con el nombre "{nombre}"'
                    }
                rol.name = nombre

            # Actualizar permisos si se proporcionan
            if permisos_ids is not None:
                permisos = Permission.objects.filter(id__in=permisos_ids)
                rol.permissions.set(permisos)

            rol.save()

            print(f"✓ Rol actualizado: {rol.name}")

            return {
                'success': True,
                'rol_id': rol.id,
                'nombre': rol.name,
                'mensaje': f'Rol actualizado exitosamente'
            }

        except Group.DoesNotExist:
            return {
                'success': False,
                'error': f'El rol con ID {rol_id} no existe'
            }
        except Exception as e:
            print(f"Error actualizando rol: {str(e)}")
            return {
                'success': False,
                'error': f'Error actualizando rol: {str(e)}'
            }

    @staticmethod
    def eliminar_rol(rol_id):
        """Elimina un rol"""
        from django.contrib.auth.models import Group

        try:
            rol = Group.objects.get(id=rol_id)
            nombre = rol.name
            rol.delete()

            print(f"✓ Rol eliminado: {nombre}")

            return {
                'success': True,
                'mensaje': f'Rol "{nombre}" eliminado exitosamente'
            }

        except Group.DoesNotExist:
            return {
                'success': False,
                'error': f'El rol con ID {rol_id} no existe'
            }
        except Exception as e:
            print(f"Error eliminando rol: {str(e)}")
            return {
                'success': False,
                'error': f'Error eliminando rol: {str(e)}'
            }


class PermisoService:
    """Servicio para obtener permisos disponibles"""

    @staticmethod
    def obtener_permisos_disponibles():
        """Obtiene todos los permisos disponibles"""
        from django.contrib.auth.models import Permission

        permisos = Permission.objects.all()

        resultado = []
        for permiso in permisos:
            resultado.append({
                'id': permiso.id,
                'nombre': permiso.name,
                'codigo': permiso.codename,
                'app': permiso.content_type.app_label,
                'modelo': permiso.content_type.model
            })

        return resultado

    @staticmethod
    def obtener_permisos_por_app():
        """Obtiene permisos agrupados por aplicación"""
        from django.contrib.auth.models import Permission

        permisos = Permission.objects.all().select_related('content_type')

        resultado = {}
        for permiso in permisos:
            app = permiso.content_type.app_label

            if app not in resultado:
                resultado[app] = []

            resultado[app].append({
                'id': permiso.id,
                'nombre': permiso.name,
                'codigo': permiso.codename,
                'modelo': permiso.content_type.model
            })

        return resultado
