import cloudinary
import cloudinary.uploader
from django.conf import settings
import os


class CloudinaryService:
    """
    Servicio para subir archivos a Cloudinary.
    """
    
    _configured = False
    
    @classmethod
    def configure(cls):
        """Configura Cloudinary con las credenciales del proyecto"""
        if cls._configured:
            return
            
        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', None)
        api_key = getattr(settings, 'CLOUDINARY_API_KEY', None)
        api_secret = getattr(settings, 'CLOUDINARY_API_SECRET', None)
        
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            cls._configured = True
    
    @classmethod
    def upload_image(cls, file, folder='tienda/productos', public_id=None):
        """
        Sube una imagen a Cloudinary.
        
        Args:
            file: Archivo a subir (InMemoryUploadedFile)
            folder: Carpeta en Cloudinary
            public_id: ID público opcional para el recurso
            
        Returns:
            dict: {
                'url': str,
                'public_id': str,
                'secure_url': str,
                'format': str,
                'width': int,
                'height': int
            }
        """
        cls.configure()
        
        upload_kwargs = {
            'folder': folder,
            'resource_type': 'image',
            'transformation': [
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        }
        
        if public_id:
            upload_kwargs['public_id'] = public_id
        
        result = cloudinary.uploader.upload(file, **upload_kwargs)
        
        return {
            'url': result.get('url'),
            'public_id': result.get('public_id'),
            'secure_url': result.get('secure_url'),
            'format': result.get('format'),
            'width': result.get('width'),
            'height': result.get('height')
        }
    
    @classmethod
    def delete_image(cls, public_id):
        """
        Elimina una imagen de Cloudinary.
        
        Args:
            public_id: ID público del recurso
            
        Returns:
            dict: Resultado de la eliminación
        """
        cls.configure()
        return cloudinary.uploader.destroy(public_id)
    
    @classmethod
    def get_image_url(cls, public_id, transformation=None):
        """
        Obtiene la URL optimizada de una imagen.
        
        Args:
            public_id: ID público del recurso
            transformation: Transformaciones opcionales
            
        Returns:
            str: URL de la imagen
        """
        cls.configure()
        
        kwargs = {'resource_type': 'image'}
        if transformation:
            kwargs['transformation'] = transformation
            
        return cloudinary.url(public_id, **kwargs)