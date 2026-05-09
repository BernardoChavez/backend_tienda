import requests
import json
import re
import time
from ..config_reportes import REPORT_CONFIG


class LLMTraductorReportes:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openrouter/free"

    def traducir_texto_a_json(self, texto_usuario: str) -> dict:
        vistas = list(REPORT_CONFIG["modelos"].keys())
        mapa_campos = REPORT_CONFIG["mapa_campos"]

        prompt = self._construir_prompt(vistas, mapa_campos, texto_usuario)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        ultimo_error = None
        for intento in range(3):
            try:
                response = requests.post(self.url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()

                res_json = response.json()
                raw_content = res_json['choices'][0]['message']['content']

                clean_content = re.sub(r'```json|```', '', raw_content).strip()
                resultado = json.loads(clean_content)

                return self._validar_payload(resultado, mapa_campos)

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else 0
                if status_code == 429:
                    espera = (intento + 1) * 3
                    print(f"[DEBUG LLM] Rate limited (429), reintentando en {espera}s (intento {intento + 1}/3)")
                    time.sleep(espera)
                    ultimo_error = e
                    continue
                raise Exception(f"Error HTTP {status_code} de la IA: {str(e)}")
            except requests.exceptions.Timeout:
                espera = (intento + 1) * 3
                print(f"[DEBUG LLM] Timeout, reintentando en {espera}s (intento {intento + 1}/3)")
                time.sleep(espera)
                ultimo_error = e
                continue
            except json.JSONDecodeError as e:
                raise Exception(f"La IA devolvió un formato inválido: {str(e)}")
            except Exception as e:
                raise Exception(f"Falla en la comunicación con la IA: {str(e)}")

        raise Exception(f"La IA no respondió después de 3 intentos. Último error: {str(ultimo_error)}")

    def _construir_prompt(self, vistas, mapa_campos, texto_usuario) -> str:
        ejemplos = self._obtener_ejemplos()
        combinaciones = self._obtener_combinaciones()
        capacidades = self._obtener_capacidades()

        return f"""Eres un traductor de lenguaje natural a JSON para un sistema de reportes de e-commerce.

{capacidades}

{combinaciones}

VISTAS DISPONIBLES: {vistas}

CAMPOS POR VISTA:
{json.dumps(mapa_campos, indent=2, ensure_ascii=False)}

{ejemplos}

REGLAS OBLIGATORIAS:
1. Devuelve SOLO el JSON. Sin explicaciones, sin texto adicional.
2. El JSON debe tener la estructura correcta con todos los campos requeridos.
3. Usa 'vista_logica' con un valor de las VISTAS DISPONIBLES.
4. Los campos en 'agrupar_por', 'filtros' y 'metricas_agrupadas' deben existir en CAMPOS POR VISTA.
5. Para filtros de fecha usa: month, year, day como operador.
6. Para filtros de agrupacion usa 'filtros_having'.
7. Para ranking/posicion usa 'ventana' con 'funcion': RANK o ROW_NUMBER.
8. Los operadores de metricas son: sum, count, avg, min, max.
9. Ordenar: campo normal para ascendente, -campo para descendente.

PETICIÓN DEL USUARIO: "{texto_usuario}"

Responde SOLO con el JSON."""

    def _obtener_capacidades(self) -> str:
        return """CAPACIDADES DEL MOTOR:
- GROUP BY: usa 'agrupar_por' con lista de campos
- Agregaciones: 'metricas_agrupadas' [{campo, operacion, alias}]
- Operadores: sum, count, avg, min, max
- Filtros WHERE: 'filtros' [{campo, operador, valor}]
- Operadores fecha: exact, month, year, day, gte, lte, gt, lt
- Filtros HAVING: 'filtros_having' [{alias, operador, valor}]
- Funciones ventana: 'ventana' {funcion, partition_by, orden, alias}
- Funciones ventana: RANK, ROW_NUMBER, LAG, LEAD
- Ordenamiento: 'ordenar_por' (campo o -campo)
- Paginación: 'paginacion' {pagina, cantidad_por_pagina}"""

    def _obtener_combinaciones(self) -> str:
        return """COMBINACIONES VÁLIDAS DE TABLAS:

 - detalle_venta: acceso a cliente_nombre, cliente_apellido, producto_nombre, categoria_nombre, marca_nombre, venta_fecha
  Útil para: productos más vendidos, clientes por cantidad comprada, ventas por categoría, ranking

 - venta: acceso a cliente_nombre, cliente_apellido, estado, tipo
  Útil para: clientes por gasto, ventas por tipo/estado

 - detalle_compra: acceso a proveedor_nombre, compra_fecha, producto_nombre, categoria_nombre
  Útil para: compras por producto, proveedores más comprados, gastos por proveedor

 - producto: acceso a categoria_nombre, marca_nombre, activo
  Útil para: inventario por categoría/marca, productos activos

 - cliente: acceso a username, nombre, apellido, email

ATENCIÓN: Las vistas 'categoria' y 'marca' NO existen. Usa detalle_venta o producto para reportes que involucren categorías o marcas."""

    def _obtener_ejemplos(self) -> str:
        return """EJEMPLOS DE PAYLOADS VÁLIDOS:

1. "Los 10 productos más vendidos de mayo":
{{
  "vista_logica": "detalle_venta",
  "agrupar_por": ["producto_id", "producto_nombre", "categoria_nombre"],
  "metricas_agrupadas": [
    {{"campo": "cantidad", "operacion": "sum", "alias": "total_vendido"}},
    {{"campo": "precio_subtotal", "operacion": "sum", "alias": "ingresos"}}
  ],
  "filtros": [
    {{"campo": "venta_fecha", "operador": "month", "valor": 5}},
    {{"campo": "venta_estado", "operador": "exact", "valor": "completado"}}
  ],
  "ordenar_por": "-total_vendido",
  "paginacion": {{"pagina": 1, "cantidad_por_pagina": 10}}
}}

2. "Clientes ordenados por gasto total":
{{
  "vista_logica": "venta",
  "agrupar_por": ["usuario_id", "cliente_nombre", "cliente_apellido"],
  "metricas_agrupadas": [
    {{"campo": "precio_total", "operacion": "sum", "alias": "total_gastado"}},
    {{"campo": "id", "operacion": "count", "alias": "num_ventas"}}
  ],
  "filtros": [{{"campo": "estado", "operador": "exact", "valor": "completado"}}],
  "ordenar_por": "-total_gastado"
}}

3. "Categorías con más de $5000 en ventas":
{{
  "vista_logica": "detalle_venta",
  "agrupar_por": ["categoria_id", "categoria_nombre"],
  "metricas_agrupadas": [
    {{"campo": "precio_subtotal", "operacion": "sum", "alias": "ingresos"}}
  ],
  "filtros": [{{"campo": "venta_estado", "operador": "exact", "valor": "completado"}}],
  "filtros_having": [{{"alias": "ingresos", "operador": "gte", "valor": 5000}}],
  "ordenar_por": "-ingresos"
}}

4. "Top 3 productos por categoría":
{{
  "vista_logica": "detalle_venta",
  "agrupar_por": ["producto_id", "producto_nombre", "categoria_nombre"],
  "metricas_agrupadas": [
    {{"campo": "cantidad", "operacion": "sum", "alias": "total_vendido"}}
  ],
  "filtros": [{{"campo": "venta_estado", "operador": "exact", "valor": "completado"}}],
  "ordenar_por": "-total_vendido",
  "ventana": {{
    "funcion": "ROW_NUMBER",
    "partition_by": ["categoria_id"],
    "orden": "-total_vendido",
    "alias": "posicion"
  }}
}}

5. "Ventas de hoy":
{{
  "vista_logica": "venta",
  "filtros": [{{"campo": "fecha", "operador": "gte", "valor": "2025-05-09"}}],
  "ordenar_por": "-fecha"
}}

6. "Proveedores más comprados":
{{
  "vista_logica": "compra",
  "agrupar_por": ["proveedor_id", "proveedor_nombre"],
  "metricas_agrupadas": [
    {{"campo": "total", "operacion": "sum", "alias": "total_comprado"}},
    {{"campo": "id", "operacion": "count", "alias": "num_compras"}}
  ],
  "ordenar_por": "-total_comprado"
}}

8. "Ganancias del mes por categoría":
{{
  "vista_logica": "detalle_venta",
  "agrupar_por": ["categoria_id", "categoria_nombre"],
  "metricas_agrupadas": [
    {{"campo": "ganancia", "operacion": "sum", "alias": "ganancia_total"}}
  ],
  "filtros": [{{"campo": "venta_fecha", "operador": "month", "valor": 5}}],
  "ordenar_por": "-ganancia_total"
}}"""

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