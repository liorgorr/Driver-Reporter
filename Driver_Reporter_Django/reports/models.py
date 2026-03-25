from django.db import models


class Report(models.Model):
    user_name = models.CharField(max_length=150)
    plate_number = models.CharField(max_length=20, blank=True, default='')
    offense_type = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    latitude_coordinate = models.FloatField()
    longitude_coordinate = models.FloatField()

    def __str__(self):
        return f"{self.offense_type} | {self.plate_number} | {self.date}"

    class Meta:
        db_table = 'report'
