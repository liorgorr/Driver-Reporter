from django.urls import path
from .views import AuthStatusView, AuthCsrfView, AuthSignupView, AuthCookieLoginView, AuthCookieLogoutView, MaxReportedPlateView, ReportCreateView, DistinctPlateCountView, ReportCountView, ReportsByPlateView, MaxReportedTypeView, AllReportsView, CheckUsernameView, CurrentUserReportsView, PasswordChangeView

urlpatterns = [
    path('auth/csrf/', AuthCsrfView.as_view(), name='auth-csrf'),
    path('auth/check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('auth/signup/', AuthSignupView.as_view(), name='auth-signup'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('auth/status/', AuthStatusView.as_view(), name='auth-status'),
    path('auth/login/', AuthCookieLoginView.as_view(), name='auth-login'),
    path('auth/logout/', AuthCookieLogoutView.as_view(), name='auth-logout'),
    path('reports/create/', ReportCreateView.as_view(), name='report-create'),
    path('reports/users/me/', CurrentUserReportsView.as_view(), name='current-user-reports'),
    path('reports/distinct-plate-count/', DistinctPlateCountView.as_view(), name='distinct-plate-count'),
    path('reports/count/', ReportCountView.as_view(), name='count'),
    path('reports/max-reported-plate/', MaxReportedPlateView.as_view(), name='max-reported-plate'),
    path('reports/plates/<str:plate_number>/', ReportsByPlateView.as_view(), name='reports-by-plate'),
    path('reports/max-reported-type/', MaxReportedTypeView.as_view(), name='max-reported-type'),
    path('reports/all/', AllReportsView.as_view(), name='all-reports'),
]
