import base64

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from django.core.management.base import BaseCommand


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


class Command(BaseCommand):
    help = 'Genera claves VAPID para Web Push.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='admin@tienda.com',
            help='Email de contacto para VAPID_ADMIN_EMAIL.',
        )

    def handle(self, *args, **options):
        private_key = ec.generate_private_key(ec.SECP256R1())
        private_value = private_key.private_numbers().private_value
        private_raw = private_value.to_bytes(32, 'big')
        public_raw = private_key.public_key().public_bytes(
            Encoding.X962,
            PublicFormat.UncompressedPoint,
        )

        self.stdout.write('Copia estas variables en tu .env o en las variables del despliegue:\n')
        self.stdout.write(f"VAPID_PUBLIC_KEY={b64url(public_raw)}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={b64url(private_raw)}")
        self.stdout.write(f"VAPID_ADMIN_EMAIL={options['email']}")
