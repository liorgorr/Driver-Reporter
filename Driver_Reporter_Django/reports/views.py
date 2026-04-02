from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DataError, IntegrityError
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.models import Token
from .models import Report
from .serializers import ReportSerializer
from .throttles import LoginRateThrottle


def _get_valid_token_from_cookie(request):
    auth_token = request.COOKIES.get('authToken')
    if not auth_token:
        return None

    try:
        token = Token.objects.select_related('user').get(key=auth_token)
    except Token.DoesNotExist:
        return None

    token_ttl = getattr(settings, 'AUTH_TOKEN_TTL_SECONDS', 3600)
    if timezone.now() - token.created > timedelta(seconds=token_ttl):
        token.delete()
        return None

    return token

def _get_authenticated_user_from_cookie(request):
    token = _get_valid_token_from_cookie(request)
    if token is None:
        return None
    return token.user


def _enforce_csrf(request):
    failure = CsrfViewMiddleware(lambda req: None).process_view(
        request,
        lambda req: None,
        (),
        {},
    )
    if failure is not None:
        return Response({'detail': 'CSRF validation failed.'}, status=status.HTTP_403_FORBIDDEN)
    return None


class AuthStatusView(APIView):
    """
    GET /api/v1/auth/status/ — check if user is authenticated (verifies HttpOnly cookie token)
    """
    def get(self, request):
        user = _get_authenticated_user_from_cookie(request)
        if user is None:
            return Response({'authenticated': False}, status=status.HTTP_200_OK)

        return Response({'authenticated': True, 'username': user.username}, status=status.HTTP_200_OK)


class AuthCsrfView(APIView):
    """
    GET /api/v1/auth/csrf/ — issue CSRF cookie for SPA requests
    """
    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request)
        return Response({'detail': 'CSRF cookie set.'}, status=status.HTTP_200_OK)


class AuthSignupView(APIView):
    """
    POST /api/v1/auth/signup/ — create a new user account
    """
    permission_classes = [AllowAny]

    def post(self, request):
        csrf_failure = _enforce_csrf(request)
        if csrf_failure is not None:
            return csrf_failure

        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        if not username:
            return Response({'username': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({'password': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        username_field = User._meta.get_field('username')
        try:
            username_field.run_validators(username)
        except DjangoValidationError as exc:
            return Response({'username': list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response(
                {'username': ['A user with that username already exists.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password, user=User(username=username))
        except DjangoValidationError as exc:
            return Response({'password': list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)
     
        User.objects.create_user(username=username, password=password)
        return Response({'detail': 'User created successfully.'}, status=status.HTTP_201_CREATED)


class AuthCookieLoginView(APIView):
    """
    POST /api/v1/auth/login/ — authenticate and set auth token in an HttpOnly cookie
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        csrf_failure = _enforce_csrf(request)
        if csrf_failure is not None:
            return csrf_failure

        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        response = Response({'detail': 'Login successful.'}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='authToken',
            value=token.key,
            max_age=settings.AUTH_TOKEN_TTL_SECONDS,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Strict',
            path='/',
        )
        return response


class AuthCookieLogoutView(APIView):
    """
    POST /api/v1/auth/logout/ — clear auth cookie and invalidate token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        csrf_failure = _enforce_csrf(request)
        if csrf_failure is not None:
            return csrf_failure

        auth_token = request.COOKIES.get('authToken')
        if auth_token:
            Token.objects.filter(key=auth_token).delete()

        response = Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)
        response.delete_cookie(
            key='authToken',
            path='/',
            samesite='Strict',
        )
        return response

class CheckUsernameView(APIView):
    """
    GET /api/v1/auth/check-username/?username=<username> — check if a username is available
    """
    def get(self, request):
        username = (request.query_params.get('username') or '').strip()
        exists = User.objects.filter(username=username).exists()
        return Response({'available': not exists})


class PasswordChangeView(APIView):
    """
    PUT /api/v1/auth/change-password/ — change current authenticated user's password
    """
    permission_classes = [AllowAny]

    def put(self, request):
        csrf_failure = _enforce_csrf(request)
        if csrf_failure is not None:
            return csrf_failure

        token = _get_valid_token_from_cookie(request)
        if token is None:
            return Response({'detail': 'Invalid or expired auth token.'}, status=status.HTTP_401_UNAUTHORIZED)

        new_password = (request.data.get('password') or '')
        if not new_password:
            return Response({'detail': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            return Response({'password': list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        Token.objects.filter(user=user).delete()
        refreshed_token = Token.objects.create(user=user)

        response = Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='authToken',
            value=refreshed_token.key,
            max_age=settings.AUTH_TOKEN_TTL_SECONDS,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Strict',
            path='/',
        )
        return response

class ReportCreateView(APIView):
    """
    POST /api/v1/reports/create/ — create a new report
    """
    def post(self, request):
        csrf_failure = _enforce_csrf(request)
        if csrf_failure is not None:
            return csrf_failure

        user = _get_authenticated_user_from_cookie(request)
        if user is None:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ReportSerializer(
            data=request.data,
            context={'authenticated_user': user},
        )
        if serializer.is_valid():
            serializer.save(user_name=user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistinctPlateCountView(APIView):
    """
    GET /api/v1/reports/distinct-plate-count/ — number of distinct non-empty plate numbers
    """
    def get(self, request):
        count = Report.objects.exclude(plate_number='').values('plate_number').distinct().count()
        return Response({'count': count})

class ReportCountView(APIView):
    """
    GET /api/v1/reports/count/ — number of reports
    """
    def get(self, request):
        count = Report.objects.count()
        return Response({'count': count})      

class MaxReportedPlateView(APIView):
    """
    GET /api/v1/reports/max-reported-plate/ — the most reported plate number (excluding empty plate numbers) and the count of its reports
    """
    def get(self, request):
        max_reported = Report.objects.exclude(plate_number='').values('plate_number').annotate(count=Count('plate_number')).order_by('-count').first()
        return Response({'maxReported': max_reported})

class ReportsByPlateView(APIView):
    """
    GET /api/v1/reports/plates/{plate_number}/ — all reports for a given plate number (excluding empty plate numbers) and the count of those reports
    """
    def get(self, request, plate_number):
        reports = Report.objects.exclude(plate_number='').filter(plate_number=plate_number)
        user = _get_authenticated_user_from_cookie(request)
        reported_by_current_user = False
        if user is not None:
            reported_by_current_user = reports.filter(user_name=user.username).exists()
        serializer = ReportSerializer(reports, many=True)
        return Response({
            'count': reports.count(),
            'reported_by_current_user': reported_by_current_user,
            'reports': serializer.data,
        })

class MaxReportedTypeView(APIView):
    """
    GET /api/v1/reports/max-reported-type/ — the most reported offense type (excluding other) and the count of its reports
    """
    def get(self, request):
        max_reported = Report.objects.exclude(offense_type='💬 אחר').values('offense_type').annotate(count=Count('offense_type')).order_by('-count').first()
        return Response({'maxReported': max_reported})


class AllReportsView(APIView):
    """
    GET /api/v1/reports/all/ — all reports with coordinates
    """
    def get(self, request):
        reports = Report.objects.exclude(latitude_coordinate__isnull=True).exclude(longitude_coordinate__isnull=True)
        serializer = ReportSerializer(reports, many=True)
        return Response({'reports': serializer.data})
       
class CurrentUserReportsView(APIView):
    """
    GET /api/v1/reports/users/me/ — all reports created by the authenticated user
    """
    def get(self, request):
        user = _get_authenticated_user_from_cookie(request)
        if user is None:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        reports = Report.objects.filter(user_name=user.username)
        serializer = ReportSerializer(reports, many=True)
        return Response({'count': reports.count(), 'reports': serializer.data})