# Generated by Django 3.2.8 on 2022-02-04 23:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zoomcar', '0003_auto_20220204_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='twitterTokenRefresh',
            field=models.CharField(default=None, max_length=500),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='fechaReserva',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 5, 0, 30, 48, 279906)),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='twitterToken',
            field=models.CharField(default=None, max_length=500),
        ),
    ]
