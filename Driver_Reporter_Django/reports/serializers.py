from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id',
            'user_name',
            'plate_number',
            'offense_type_name',
            'date',
            'time',
            'description',
            'latitude_coordinate',
            'longitude_coordinate',
        ]
        read_only_fields = ['id']
