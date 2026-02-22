from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import Report
from .serializers import ReportSerializer

class ReportCreateView(APIView):
    """
    POST /api/v1/reports/ — create a new report
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
    GET /api/v1/reports/report-count/ — number of reports
    """
    def get(self, request):
        count = Report.objects.count()
        return Response({'count': count})      

class MaxReportCountView(APIView):
    """
    GET /api/v1/reports/max-reported/ — the plate number with the most reports (excluding empty plate numbers) and the count of its reports
    """
    def get(self, request):
        max_reported = Report.objects.exclude(plate_number='').values('plate_number').annotate(count=Count('plate_number')).order_by('-count').first()
        return Response({'maxReported': max_reported})      
