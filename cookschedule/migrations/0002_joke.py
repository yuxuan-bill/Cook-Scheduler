# Generated by Django 3.0.1 on 2020-02-02 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cookschedule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Joke',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=16)),
                ('setup', models.CharField(max_length=1024)),
                ('punchline', models.CharField(max_length=1024)),
            ],
        ),
    ]
