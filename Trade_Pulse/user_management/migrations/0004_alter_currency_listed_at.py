# Generated by Django 4.2.7 on 2023-11-24 19:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0003_alter_currency_listed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='listed_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 24, 19, 38, 59, 772197)),
        ),
    ]