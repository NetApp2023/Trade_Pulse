# Generated by Django 4.2.5 on 2023-11-04 21:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='uuid',
            field=models.CharField(default=0, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='listed_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 4, 17, 50, 52, 205955)),
        ),
    ]
