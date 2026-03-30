import re

from rest_framework import serializers
from .models import Report


HTML_LIKE_PATTERN = re.compile(r'<[^>]*>|&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);')


def _reject_markup(value: str, field_name: str) -> str:
    if value and HTML_LIKE_PATTERN.search(value):
        raise serializers.ValidationError(
            f'{field_name} cannot contain HTML or encoded markup.'
        )
    return value


class ReportSerializer(serializers.ModelSerializer):
    MAX_DESCRIPTION_LENGTH = 300

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
        return _reject_markup(value, 'plate_number')

    def validate_offense_type(self, value):
        return _reject_markup(value, 'offense_type')

    def validate_description(self, value):
        if len(value) > self.MAX_DESCRIPTION_LENGTH:
            raise serializers.ValidationError(
                f'description cannot be longer than {self.MAX_DESCRIPTION_LENGTH} characters.'
            )
        return _reject_markup(value, 'description')
