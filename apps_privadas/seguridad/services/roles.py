from django.contrib.auth.models import Group, Permission


class RolService:
    """Servicio para operaciones con roles"""

    @staticmethod
    def crear_rol(nombre, permisos_ids=None):
        """Crea un nuevo rol"""
        try:
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
        """Obtiene informacion de un rol"""
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
                'mensaje': 'Rol actualizado exitosamente'
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

