from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_alter_report_table'),
    ]

    operations = [
        migrations.RenameField('Report', 'offense_type_name', 'offense_type'),
    ]
