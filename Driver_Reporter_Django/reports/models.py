from django.db import models


class Report(models.Model):
    user_name = models.CharField(max_length=150)
    plate_number = models.CharField(blank=True, default='')
    offense_type = models.CharField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    description = models.TextField(max_length=300, blank=True, default='')
    latitude_coordinate = models.FloatField()
    longitude_coordinate = models.FloatField()

    def __str__(self):
        return f"{self.offense_type} | {self.plate_number} | {self.date}"

    class Meta:
        db_table = 'report'
        constraints = [
            models.UniqueConstraint(
                fields=['user_name', 'plate_number'],
                condition=~models.Q(plate_number=''),
                name='uniq_report_user_plate_non_empty',
            ),
        ]
