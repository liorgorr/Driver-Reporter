import re
from calendar import monthrange
from datetime import datetime
from rest_framework import serializers
from django.utils import timezone
from .models import Report

HTML_LIKE_PATTERN = re.compile(r'<[^>]*>|&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);')

RED_OR_BLACK_PLATE_PATTERN = re.compile(r'^(?:מ|צ) - \d{1,7}$')
BLUE_PLATE_PATTERN = re.compile(r'^מצ - \d{1,3}$')
YELLOW_PLATE_PATTERN = re.compile(r'^\d{1,8}$')

ALLOWED_OFFENSE_TYPES = {
    '🚦 רמזור אדום',
    '📱 טלפון בנהיגה',
    '🚗💨 מהירות מסוכנת',
    '🚗↔️ עקיפה מסוכנת',
    '🚸 זכות קדימה במעבר חציה',
    '❌🅿️🚶 חניה על מדרכה/מעבר חצייה',
    '❌🅿️🚴 חניה על שביל אופניים',
    '💬 אחר',
}

def _subtract_one_month(date_time):
    year = date_time.year
    month = date_time.month - 1
    if month == 0:
        month = 12
        year -= 1

    day = min(date_time.day, monthrange(year, month)[1])
    return date_time.replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)

def _reject_markup(value: str, field_name: str) -> str:
    if value and HTML_LIKE_PATTERN.search(value):
        raise serializers.ValidationError(
            f'{field_name} cannot contain HTML or encoded markup.'
        )
    return value

class ReportSerializer(serializers.ModelSerializer):
    MAX_DESCRIPTION_LENGTH = 300
    MIN_LATITUDE = 29.49
    MAX_LATITUDE = 33.34
    MIN_LONGITUDE = 34.266
    MAX_LONGITUDE = 35.9

    class Meta:
        model = Report
        fields = [
            'id',
            'plate_number',
            'offense_type',
            'date',
            'time',
            'description',
            'latitude_coordinate',
            'longitude_coordinate',
        ]
        read_only_fields = ['id']

    def validate_plate_number(self, value):
        value = _reject_markup(value.strip(), 'plate_number')
        if not value:
            return value

        if YELLOW_PLATE_PATTERN.fullmatch(value):
            return value

        if RED_OR_BLACK_PLATE_PATTERN.fullmatch(value):
            return value

        if BLUE_PLATE_PATTERN.fullmatch(value):
            return value

        raise serializers.ValidationError(
            'plate_number format is invalid.'
        )

    def validate_offense_type(self, value):
        value = _reject_markup(value.strip(), 'offense_type')

        if value not in ALLOWED_OFFENSE_TYPES:
            raise serializers.ValidationError('offense_type is invalid.')

        return value

    def validate_description(self, value):
        value = _reject_markup(value, 'description')
        if len(value) > self.MAX_DESCRIPTION_LENGTH:
            raise serializers.ValidationError(
                f'description cannot be longer than {self.MAX_DESCRIPTION_LENGTH} characters.'
            )
        
        return value

    def validate_latitude_coordinate(self, value):
        if not self.MIN_LATITUDE <= value <= self.MAX_LATITUDE:
            raise serializers.ValidationError(
                f'latitude_coordinate must be between {self.MIN_LATITUDE} and {self.MAX_LATITUDE}.'
            )
        return value

    def validate_longitude_coordinate(self, value):
        if not self.MIN_LONGITUDE <= value <= self.MAX_LONGITUDE:
            raise serializers.ValidationError(
                f'longitude_coordinate must be between {self.MIN_LONGITUDE} and {self.MAX_LONGITUDE}.'
            )
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        offense_type = attrs.get('offense_type', '')
        description = (attrs.get('description') or '').strip()

        if offense_type == '💬 אחר' and not description:
            raise serializers.ValidationError(
                {'description': ['description is required when offense_type is other.']}
            )

        report_date = attrs.get('date')
        report_time = attrs.get('time')
        if report_date is None:
                raise serializers.ValidationError({'date': ['date is required.']})  
        else:
            date_time = datetime.combine(report_date, report_time or datetime.min.time())
            current_timezone = timezone.get_current_timezone()
            report_date_time = timezone.make_aware(date_time, current_timezone)
            now = timezone.localtime(timezone.now(), current_timezone)

            if report_date_time > now:
                raise serializers.ValidationError({'date': ['date/time cannot be in the future.']})

            one_month_ago = _subtract_one_month(now)
            
            if report_date_time < one_month_ago:
                raise serializers.ValidationError(
                    {'date': ['date/time cannot be older than one month.']}
                )

        return attrs