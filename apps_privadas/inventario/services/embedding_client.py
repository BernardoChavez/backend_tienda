import requests
from django.conf import settings


def obtener_embedding(nombre, descripcion, categoria, marca):
    url = settings.EMBEDDING_SERVICE_URL
    if not url:
        raise ValueError("EMBEDDING_SERVICE_URL no está configurado")

    texto = f"Producto: {nombre}\nMarca: {marca}\nCategoría: {categoria}\nDescripción: {descripcion}"

    resp = requests.post(
        f"{url}/api/vectorize",
        json={"text": texto},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]
