from ..config_reportes import REPORT_CONFIG
from typing import Dict, Any, Union, List
from django.db.models import QuerySet, Sum, Count, F, Q, Value, Window
from django.db.models.functions import Rank, RowNumber, Lag, Lead, Coalesce
from django.db.models import Avg, Min, Max
from django.core.paginator import Paginator


class MotorReportesDinamicos:
    def __init__(self):
        self.modelos = REPORT_CONFIG["modelos"]
        self.mapa_campos = REPORT_CONFIG["mapa_campos"]

    def procesar_reporte(self, payload: Dict[str, Any]) -> Union[List[Dict], Dict]:
        vista_logica = payload.get("vista_logica")
        queryset = self._obtener_queryset_base(vista_logica)
        campos = self.mapa_campos.get(vista_logica, {})

        queryset = self._aplicar_select_related(queryset, campos, payload)

        queryset = self._aplicar_filtros_where(queryset, payload, campos)

        agrupar_por = payload.get("agrupar_por", [])
        metricas = payload.get("metricas_agrupadas", [])

        if agrupar_por and metricas:
            queryset = self._aplicar_agrupacion(queryset, agrupar_por, metricas, campos)
        elif metricas:
            queryset = self._aplicar_anotaciones_simples(queryset, metricas, campos)

        filtros_having = payload.get("filtros_having", [])
        if filtros_having and agrupar_por:
            queryset = self._aplicar_filtros_having(queryset, filtros_having)

        ventana = payload.get("ventana", {})
        if ventana:
            queryset = self._aplicar_funciones_ventana(queryset, ventana, campos)

        ordenar_por = payload.get("ordenar_por")
        if ordenar_por:
            queryset = self._aplicar_ordenamiento(queryset, ordenar_por, campos)

        return self._finalizar_paginacion(queryset, payload.get("paginacion", {}))

    def _obtener_queryset_base(self, vista_logica: str) -> QuerySet:
        if not vista_logica or vista_logica not in self.modelos:
            raise ValueError(f"Vista logica '{vista_logica}' no configurada")

        Modelo = self.modelos[vista_logica]
        return Modelo.objects.all()

    def _aplicar_select_related(self, queryset, campos, payload):
        agrupar_por = payload.get("agrupar_por", [])
        filtros = payload.get("filtros", [])

        relaciones_necesarias = set()
        todos_campos = list(agrupar_por) + [f.get("campo") for f in filtros if f.get("campo")]

        for campo in todos_campos:
            if campo:
                campo_real = campos.get(campo, campo)
                partes = campo_real.split("__")
                if len(partes) > 1:
                    for i in range(len(partes) - 1):
                        relaciones_necesarias.add("__".join(partes[:i+1]))

        if relaciones_necesarias:
            queryset = queryset.select_related(*relaciones_necesarias)

        return queryset

    def _aplicar_filtros_where(self, queryset, payload, campos) -> QuerySet:
        query_final = Q()

        for filtro in payload.get("filtros", []):
            campo = filtro.get("campo")
            operador = filtro.get("operador", "exact")
            valor = filtro.get("valor")

            if not campo:
                continue

            campo_real = campos.get(campo, campo)
            lookup = f"{campo_real}__{operador}"

            query_final &= Q(**{lookup: valor})

        filtros_avanzados = payload.get("filtros_avanzados", {})
        if filtros_avanzados:
            bloque = self._construir_bloque_avanzado(filtros_avanzados, campos)
            query_final &= bloque

        return queryset.filter(query_final).distinct()

    def _construir_bloque_avanzado(self, filtros_avanzados, campos) -> Q:
        operador_logico = filtros_avanzados.get("operador_logico", "AND")
        condiciones = filtros_avanzados.get("condiciones", [])

        bloque = Q()
        for cond in condiciones:
            campo = cond.get("campo")
            operador = cond.get("operador", "exact")
            valor = cond.get("valor")

            if not campo:
                continue

            campo_real = campos.get(campo, campo)
            lookup = f"{campo_real}__{operador}"

            if operador_logico == "OR":
                bloque |= Q(**{lookup: valor})
            else:
                bloque &= Q(**{lookup: valor})

        return bloque

    def _aplicar_agrupacion(self, queryset, agrupar_por, metricas, campos) -> QuerySet:
        campos_agrupacion = [campos.get(c, c) for c in agrupar_por]
        anotaciones = {}

        for metrica in metricas:
            campo = metrica.get("campo")
            operacion = metrica.get("operacion", "sum")
            alias = metrica.get("alias", f"{campo}_{operacion}")

            campo_real = campos.get(campo, campo)

            if operacion == "sum":
                anotaciones[alias] = Sum(campo_real)
            elif operacion == "count":
                anotaciones[alias] = Count(campo_real)
            elif operacion == "avg":
                anotaciones[alias] = Avg(campo_real)
            elif operacion == "min":
                anotaciones[alias] = Min(campo_real)
            elif operacion == "max":
                anotaciones[alias] = Max(campo_real)

        return queryset.values(*campos_agrupacion).annotate(**anotaciones)

    def _aplicar_anotaciones_simples(self, queryset, metricas, campos) -> QuerySet:
        anotaciones = {}

        for metrica in metricas:
            campo = metrica.get("campo")
            operacion = metrica.get("operacion", "sum")
            alias = metrica.get("alias", f"{campo}_{operacion}")

            campo_real = campos.get(campo, campo)

            if operacion == "sum":
                anotaciones[alias] = Sum(campo_real)
            elif operacion == "count":
                anotaciones[alias] = Count(campo_real)
            elif operacion == "avg":
                anotaciones[alias] = Avg(campo_real)

        return queryset.annotate(**anotaciones)

    def _aplicar_filtros_having(self, queryset, filtros_having) -> QuerySet:
        for filtro in filtros_having:
            alias = filtro.get("alias")
            operador = filtro.get("operador", "gte")
            valor = filtro.get("valor")

            if alias and operador == "gte":
                queryset = queryset.filter(**{f"{alias}__gte": valor})
            elif alias and operador == "lte":
                queryset = queryset.filter(**{f"{alias}__lte": valor})
            elif alias and operador == "exact":
                queryset = queryset.filter(**{alias: valor})
            elif alias and operador == "gt":
                queryset = queryset.filter(**{f"{alias}__gt": valor})
            elif alias and operador == "lt":
                queryset = queryset.filter(**{f"{alias}__lt": valor})
            elif alias and operador == "neq":
                queryset = queryset.exclude(**{alias: valor})

        return queryset

    def _aplicar_funciones_ventana(self, queryset, ventana, campos) -> QuerySet:
        funcion = ventana.get("funcion", "RANK")
        partition_by = ventana.get("partition_by", [])
        orden = ventana.get("orden", "-total")
        alias = ventana.get("alias", "ranking")

        particion = [campos.get(p, p) for p in partition_by] if partition_by else []

        es_desc = orden.startswith("-")
        orden_campo = orden.lstrip("-")
        orden_real = campos.get(orden_campo, orden_campo)
        if es_desc:
            orden_real = f"-{orden_real}"

        if funcion == "RANK":
            if particion:
                window = Window(expression=Rank(), partition_by=particion, order_by=orden_real)
            else:
                window = Window(expression=Rank(), order_by=orden_real)
            queryset = queryset.annotate(**{alias: window})

        elif funcion == "ROW_NUMBER":
            if particion:
                window = Window(expression=RowNumber(), partition_by=particion, order_by=orden_real)
            else:
                window = Window(expression=RowNumber(), order_by=orden_real)
            queryset = queryset.annotate(**{alias: window})

        elif funcion == "LAG":
            offset = ventana.get("offset", 1)
            default_val = ventana.get("default", 0)
            if particion:
                window = Window(
                    expression=Lag(orden_real.strip("-"), offset=offset, default=Value(default_val)),
                    partition_by=particion,
                    order_by=orden_real
                )
            else:
                window = Window(
                    expression=Lag(orden_real.strip("-"), offset=offset, default=Value(default_val)),
                    order_by=orden_real
                )
            queryset = queryset.annotate(**{alias: window})

        elif funcion == "LEAD":
            offset = ventana.get("offset", 1)
            default_val = ventana.get("default", 0)
            if particion:
                window = Window(
                    expression=Lead(orden_real.strip("-"), offset=offset, default=Value(default_val)),
                    partition_by=particion,
                    order_by=orden_real
                )
            else:
                window = Window(
                    expression=Lead(orden_real.strip("-"), offset=offset, default=Value(default_val)),
                    order_by=orden_real
                )
            queryset = queryset.annotate(**{alias: window})

        return queryset

    def _aplicar_ordenamiento(self, queryset, ordenar_por, campos) -> QuerySet:
        es_desc = ordenar_por.startswith("-")
        campo = ordenar_por.lstrip("-")
        campo_real = campos.get(campo, campo)

        if es_desc:
            campo_real = f"-{campo_real}"

        return queryset.order_by(campo_real)

    def _finalizar_paginacion(self, queryset, paginacion) -> Dict:
        pagina = paginacion.get("pagina", 1)
        cantidad = paginacion.get("cantidad_por_pagina", 50)

        paginador = Paginator(list(queryset), cantidad)
        page_obj = paginador.get_page(pagina)

        return {
            "paginacion": {
                "total_registros": paginador.count,
                "total_paginas": paginador.num_pages,
                "pagina_actual": page_obj.number,
                "tiene_anterior": page_obj.has_previous(),
                "tiene_siguiente": page_obj.has_next(),
            },
            "datos": list(page_obj.object_list)
        }