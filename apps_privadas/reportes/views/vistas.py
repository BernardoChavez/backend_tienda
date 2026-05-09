from rest_framework.views import APIView
from rest_framework.response import Response
from ..config_reportes import REPORT_CONFIG


def _inferir_tipo(campo: str) -> str:
    nombre = campo.lower()
    if any(k in nombre for k in ['id', 'precio', 'total', 'cantidad', 'costo', 'numero', 'monto']):
        return 'number'
    if any(k in nombre for k in ['fecha', 'date']):
        return 'date'
    if any(k in nombre for k in ['activo']):
        return 'boolean'
    return 'string'


def _operadores_por_tipo(tipo: str) -> list:
    comunes = ['exact', 'neq']
    if tipo == 'number':
        return comunes + ['gte', 'gt', 'lte', 'lt']
    if tipo == 'date':
        return comunes + ['gte', 'gt', 'lte', 'lt', 'month', 'year', 'day']
    if tipo == 'boolean':
        return comunes
    return comunes + ['contains', 'icontains', 'startswith']


class ReporteVistasView(APIView):
    def get(self, request):
        mapa_campos = REPORT_CONFIG["mapa_campos"]
        modelos = REPORT_CONFIG["modelos"]
        expresiones = REPORT_CONFIG.get("expresiones", {})

        vistas = []
        for nombre_vista, campos in mapa_campos.items():
            Modelo = modelos.get(nombre_vista)
            etiqueta = Modelo._meta.verbose_name if Modelo else nombre_vista

            campos_lista = []
            for campo_nombre in campos:
                tipo = _inferir_tipo(campo_nombre)
                etiqueta_campo = campo_nombre.replace('_', ' ').title()
                campos_lista.append({
                    "nombre": campo_nombre,
                    "etiqueta": etiqueta_campo,
                    "tipo": tipo,
                    "operadores": _operadores_por_tipo(tipo),
                    "agregable": tipo == 'number',
                    "agrupable": True,
                })

            expr_vista = expresiones.get(nombre_vista, {})
            for expr_nombre, expr_config in expr_vista.items():
                campos_lista.append({
                    "nombre": expr_nombre,
                    "etiqueta": expr_config.get("etiqueta", expr_nombre.replace('_', ' ').title()),
                    "tipo": expr_config.get("tipo", "number"),
                    "operadores": ["exact", "neq", "gte", "gt", "lte", "lt"],
                    "agregable": True,
                    "agrupable": False,
                })

            vistas.append({
                "nombre": nombre_vista,
                "etiqueta": str(etiqueta),
                "campos": campos_lista,
            })

        return Response({"vistas": vistas})
