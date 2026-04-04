from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_rename_offense_type_name_to_offense_type'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='report',
            constraint=models.UniqueConstraint(
                fields=('user_name', 'plate_number'),
                condition=~models.Q(plate_number=''),
                name='uniq_report_user_plate_non_empty',
            ),
        ),
    ]
