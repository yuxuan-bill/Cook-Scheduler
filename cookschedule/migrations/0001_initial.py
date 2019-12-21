# Generated by Django 3.0.1 on 2019-12-21 22:24

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('update_time', models.DateTimeField(default=datetime.datetime(2019, 12, 21, 14, 24, 0, 348495))),
                ('cancelled', models.BinaryField(default=False)),
                ('note', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Eat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookschedule.Schedule')),
            ],
        ),
        migrations.CreateModel(
            name='Cook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookschedule.Schedule')),
            ],
        ),
    ]
