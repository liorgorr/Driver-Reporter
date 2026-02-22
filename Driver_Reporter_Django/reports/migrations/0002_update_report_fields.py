from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        # Rename fields
        migrations.RenameField('Report', 'report_date', 'date'),
        migrations.RenameField('Report', 'report_time', 'time'),
        migrations.RenameField('Report', 'latitude', 'latitude_coordinate'),
        migrations.RenameField('Report', 'longitude', 'longitude_coordinate'),

        # Remove old fields
        migrations.RemoveField('Report', 'plate_color'),
        migrations.RemoveField('Report', 'offense_type'),
        migrations.RemoveField('Report', 'created_at'),

        # Add new fields
        migrations.AddField(
            model_name='Report',
            name='user_name',
            field=models.CharField(default='anonymous', max_length=150),
        ),
        migrations.AddField(
            model_name='Report',
            name='offense_type_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
