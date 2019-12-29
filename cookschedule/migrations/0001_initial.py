# Generated by Django 3.0.1 on 2019-12-29 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(choices=[('delete', 'delete'), ('update', 'update'), ('add', 'add')], max_length=6)),
                ('user', models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=150)),
                ('note_previous', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('note', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='PreviousEater',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=16)),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookschedule.ChangeLog')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousCook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=16)),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookschedule.ChangeLog')),
            ],
        ),
        migrations.CreateModel(
            name='Eater',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=30)),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookschedule.Schedule')),
            ],
        ),
        migrations.CreateModel(
            name='Cook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Bill', 'Bill'), ('Daniel', 'Daniel'), ('Darcy', 'Darcy'), ('Leo', 'Leo')], max_length=30)),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookschedule.Schedule')),
            ],
        ),
    ]
