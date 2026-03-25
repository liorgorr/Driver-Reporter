from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.authtoken.models import Token
from .models import Report
from .serializers import ReportSerializer


class AuthStatusView(APIView):
    """
    GET /api/v1/auth/status/ — check if user is authenticated (verifies HttpOnly cookie token)
    """
    def get(self, request):
        auth_token = request.COOKIES.get('authToken')
        if not auth_token:
            return Response({'authenticated': False}, status=status.HTTP_200_OK)
        
        try:
            token = Token.objects.get(key=auth_token)
            return Response({'authenticated': True, 'username': token.user.username}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'authenticated': False}, status=status.HTTP_200_OK)


class AuthCookieLoginView(APIView):
    """
    POST /api/v1/auth/login/ — authenticate and set auth token in an HttpOnly cookie
    """
    permission_classes = [AllowAny]

    def post(self, request):
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
            max_age=60*60,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/',
        )
        return response


class AuthCookieLogoutView(APIView):
    """
    POST /api/v1/auth/logout/ — clear auth cookie and invalidate token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        auth_token = request.COOKIES.get('authToken')
        if auth_token:
            Token.objects.filter(key=auth_token).delete()

        response = Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)
        response.delete_cookie(
            key='authToken',
            path='/',
            samesite='Lax',
        )
        return response

class CheckUsernameView(APIView):
    """
    GET /api/v1/auth/check-username/?username=<username> — check if a username is available
    """
    def get(self, request):
        username = request.query_params.get('username', '')
        exists = User.objects.filter(username=username).exists()
        return Response({'available': not exists})


class ReportCreateView(APIView):
    """
    POST /api/v1/reports/create/ — create a new report
    """
    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
        serializer = ReportSerializer(reports, many=True)
        return Response({'count': reports.count(), 'reports': serializer.data})

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
    GET /api/v1/reports/users/{user_name}/ — all reports created by the user
    """
    def get(self, request, user_name):
        reports = Report.objects.filter(user_name=user_name)
        serializer = ReportSerializer(reports, many=True)
        return Response({'count': reports.count(), 'reports': serializer.data})