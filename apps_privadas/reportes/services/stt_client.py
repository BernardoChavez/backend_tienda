import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def transcribir_audio(audio_bytes: bytes, filename: str) -> str:
    url = settings.STT_SERVICE_URL
    if not url:
        raise ValueError("STT_SERVICE_URL no está configurado")

    endpoint = f"{url}/api/transcribe"
    logger.info("Enviando audio a STT: %s, filename=%s, size=%d bytes",
                endpoint, filename, len(audio_bytes))

    try:
        resp = requests.post(
            endpoint,
            files={"file": (filename, audio_bytes, "audio/wav")},
            timeout=120,
        )
        logger.info("Respuesta STT: status=%d, body=%s",
                     resp.status_code, resp.text[:300])

        resp.raise_for_status()
        return resp.json()["text"]
    except requests.exceptions.RequestException as e:
        logger.exception("Error de conexión con STT: %s", endpoint)
        raise
    except (KeyError, ValueError) as e:
        logger.exception("Respuesta inesperada de STT: %s", resp.text[:500])
        raise
