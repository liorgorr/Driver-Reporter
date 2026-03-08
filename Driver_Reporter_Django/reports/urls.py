from django.urls import path
from .views import MaxReportedPlateView, ReportCreateView, DistinctPlateCountView, ReportCountView, ReportsByPlateView, MaxReportedTypeView, AllReportsView, CheckUsernameView

urlpatterns = [
    path('auth/check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('reports/create/', ReportCreateView.as_view(), name='report-create'),
    path('reports/distinct-plate-count/', DistinctPlateCountView.as_view(), name='distinct-plate-count'),
    path('reports/count/', ReportCountView.as_view(), name='count'),
    path('reports/max-reported-plate/', MaxReportedPlateView.as_view(), name='max-reported-plate'),
    path('reports/plates/<str:plate_number>/', ReportsByPlateView.as_view(), name='reports-by-plate'),
    path('reports/max-reported-type/', MaxReportedTypeView.as_view(), name='max-reported-type'),
    path('reports/all/', AllReportsView.as_view(), name='all-reports'),
]
