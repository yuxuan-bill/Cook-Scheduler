# Generated by Django 3.0.1 on 2019-12-21 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cookschedule', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cook',
            name='name',
            field=models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=16),
        ),
        migrations.AlterField(
            model_name='eat',
            name='name',
            field=models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=16),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
