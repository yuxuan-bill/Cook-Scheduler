# Generated by Django 3.0.1 on 2019-12-21 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cookschedule', '0002_auto_20191221_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
