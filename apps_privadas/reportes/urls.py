from django.urls import path
from .views.qbe import ReporteQBEView
from .views.nlp import ReporteNLPView
from .views.vistas import ReporteVistasView

urlpatterns = [
    path('reporte/qbe/', ReporteQBEView.as_view(), name='reporte-qbe'),
    path('reporte/nlp/', ReporteNLPView.as_view(), name='reporte-nlp'),
    path('reporte/vistas/', ReporteVistasView.as_view(), name='reporte-vistas'),
]