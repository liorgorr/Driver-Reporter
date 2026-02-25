from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import Report
from .serializers import ReportSerializer

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
       
