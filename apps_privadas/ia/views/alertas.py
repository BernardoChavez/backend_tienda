from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps_privadas.ia.models import AlertaReabastecimiento
from apps_privadas.ia.serializers import AlertaReabastecimientoSerializer


class AlertaReabastecimientoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AlertaReabastecimientoSerializer

    def get_queryset(self):
        qs = AlertaReabastecimiento.objects.select_related(
            'variante__producto__categoria'
        )
        leida = self.request.query_params.get('leida')
        tipo = self.request.query_params.get('tipo')
        if leida is not None:
            qs = qs.filter(leida=leida.lower() == 'true')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    @action(detail=True, methods=['patch'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        alerta = self.get_object()
        alerta.leida = True
        alerta.save()
        return Response(self.get_serializer(alerta).data)

    @action(detail=False, methods=['patch'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        total = AlertaReabastecimiento.objects.filter(leida=False).update(leida=True)
        return Response({'detalle': f'{total} alertas marcadas como leídas.'})
