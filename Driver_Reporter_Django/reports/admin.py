from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'plate_number', 'offense_type', 'date', 'time', 'description', 'latitude_coordinate', 'longitude_coordinate')
    list_filter = ('offense_type', 'date')
    search_fields = ('plate_number', 'description')
