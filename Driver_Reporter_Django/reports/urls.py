from django.urls import path
from .views import MaxReportCountView, ReportCreateView, DistinctPlateCountView, ReportCountView

urlpatterns = [
    path('reports/', ReportCreateView.as_view(), name='report-create'),
    path('reports/distinct-plate-count/', DistinctPlateCountView.as_view(), name='distinct-plate-count'),
    path('reports/report-count/', ReportCountView.as_view(), name='report-count'),
    path('reports/max-reported/', MaxReportCountView.as_view(), name='max-reported'),
]
