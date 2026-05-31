import requests
import json
import re
import time
from ..config_reportes import REPORT_CONFIG


class LLMTraductorReportes:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.modelos = [
            "openai/gpt-oss-20b:free",
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.2-3b-instruct:free",
        ]

    def traducir_texto_a_json(self, texto_usuario: str) -> dict:
        vistas = list(REPORT_CONFIG["modelos"].keys())
        mapa_campos = REPORT_CONFIG["mapa_campos"]

        prompt = self._construir_prompt(vistas, mapa_campos, texto_usuario)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }

        ultimo_error = None
        for modelo in self.modelos:
            payload = {
                "model": modelo,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }

            try:
                print(f"[DEBUG LLM] Intentando modelo: {modelo}")
                start = time.time()
                response = requests.post(self.url, headers=headers, json=payload, timeout=60)
                elapsed = time.time() - start
                print(f"[TIMING LLM] {modelo} respondió en {elapsed:.2f}s (status={response.status_code})")

                response.raise_for_status()

                res_json = response.json()
                raw_content = res_json['choices'][0]['message']['content']

                clean_content = re.sub(r'```json|```', '', raw_content).strip()
                resultado = json.loads(clean_content)

                return self._validar_payload(resultado, mapa_campos)

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else 0
                print(f"[WARN LLM] {modelo} falló con HTTP {status_code}: {e}")
                ultimo_error = e
                continue
            except requests.exceptions.Timeout:
                print(f"[WARN LLM] {modelo} excedió timeout de 60s")
                ultimo_error = e
                continue
            except json.JSONDecodeError as e:
                print(f"[WARN LLM] {modelo} devolvió JSON inválido: {e}")
                ultimo_error = e
                continue
            except Exception as e:
                print(f"[WARN LLM] {modelo} falló: {e}")
                ultimo_error = e
                continue

        raise Exception(f"Todos los modelos fallaron. Último error: {ultimo_error}")

    def _construir_prompt(self, vistas, mapa_campos, texto_usuario) -> str:
        ejemplos = self._obtener_ejemplos()
        return f"""Eres un traductor de lenguaje natural a JSON para un sistema de reportes de e-commerce.

CAPACIDADES DEL MOTOR:
- GROUP BY: usa 'agrupar_por' con lista de campos
- Agregaciones: 'metricas_agrupadas' [{{campo, operacion, alias}}]
- Operadores: sum, count, avg, min, max
- Filtros WHERE: 'filtros' [{{campo, operador, valor}}]
- Operadores fecha: exact, month, year, day, gte, lte, gt, lt
- Filtros HAVING: 'filtros_having' [{{alias, operador, valor}}]
- Ventana: 'ventana' {{funcion, partition_by, orden, alias}} con RANK o ROW_NUMBER
- Orden: campo (asc) o -campo (desc)
- Paginacion: 'paginacion' {{pagina, cantidad_por_pagina}}

VISTAS DISPONIBLES: {vistas}

CAMPOS POR VISTA:
{json.dumps(mapa_campos, indent=2, ensure_ascii=False)}

{ejemplos}

REGLAS OBLIGATORIAS:
1. Devuelve SOLO el JSON. Sin explicaciones.
2. Usa 'vista_logica' de las VISTAS DISPONIBLES.
3. Los campos deben existir en CAMPOS POR VISTA.
4. Operadores: sum, count, avg, min, max.
5. Filtros fecha: month, year, day.
6. Para posicion/ranking: 'ventana' con funcion RANK o ROW_NUMBER.

PETICIÓN DEL USUARIO: "{texto_usuario}"

Responde SOLO con el JSON."""

    def _obtener_ejemplos(self) -> str:
        return """EJEMPLOS:

1. "Los 10 productos mas vendidos de mayo":
{
  "vista_logica": "detalle_venta",
  "agrupar_por": ["producto_id", "producto_nombre", "categoria_nombre"],
  "metricas_agrupadas": [
    {"campo": "cantidad", "operacion": "sum", "alias": "total_vendido"},
    {"campo": "precio_subtotal", "operacion": "sum", "alias": "ingresos"}
  ],
  "filtros": [
    {"campo": "venta_fecha", "operador": "month", "valor": 5},
    {"campo": "venta_estado", "operador": "exact", "valor": "completado"}
  ],
  "ordenar_por": "-total_vendido",
  "paginacion": {"pagina": 1, "cantidad_por_pagina": 10}
}

2. "Ventas de hoy":
{
  "vista_logica": "venta",
  "filtros": [{"campo": "fecha", "operador": "gte", "valor": "2025-05-09"}],
  "ordenar_por": "-fecha"
}

3. "Top 3 productos por categoria":
{
  "vista_logica": "detalle_venta",
  "agrupar_por": ["producto_id", "producto_nombre", "categoria_nombre"],
  "metricas_agrupadas": [
    {"campo": "cantidad", "operacion": "sum", "alias": "total_vendido"}
  ],
  "filtros": [{"campo": "venta_estado", "operador": "exact", "valor": "completado"}],
  "ordenar_por": "-total_vendido",
  "ventana": {
    "funcion": "ROW_NUMBER",
    "partition_by": ["categoria_id"],
    "orden": "-total_vendido",
    "alias": "posicion"
  }
}"""

    def _validar_payload(self, payload: dict, mapa_campos: dict) -> dict:
        from ..config_reportes import REPORT_CONFIG
        vista_logica = payload.get("vista_logica")

        if not vista_logica:
            raise Exception("La IA no especificó vista_logica")

        if vista_logica not in mapa_campos:
            raise Exception(f"Vista '{vista_logica}' no existe. Válidas: {list(mapa_campos.keys())}")

        campos_disponibles = set(mapa_campos.get(vista_logica, {}).keys())
        expresiones = REPORT_CONFIG.get("expresiones", {})
        expr_vista = expresiones.get(vista_logica, {})
        campos_disponibles.update(expr_vista.keys())

        agrupar_por = payload.get("agrupar_por", [])
        for campo in agrupar_por:
            if campo not in campos_disponibles:
                raise Exception(f"Campo '{campo}' no existe en '{vista_logica}'. Disponibles: {campos_disponibles}")

        filtros = payload.get("filtros", [])
        for filtro in filtros:
            campo = filtro.get("campo")
            if campo and campo not in campos_disponibles:
                raise Exception(f"Campo '{campo}' no existe en '{vista_logica}'")

        metricas = payload.get("metricas_agrupadas", [])
        for metrica in metricas:
            operacion = metrica.get("operacion")
            if operacion not in ["sum", "count", "avg", "min", "max"]:
                raise Exception(f"Operación '{operacion}' inválida. Válidas: sum, count, avg, min, max")

        return payload
