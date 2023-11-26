# Generated by Django 4.2.5 on 2023-11-26 03:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptocurrency',
            name='market_cap',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cryptocurrency',
            name='volume',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='currency',
            name='listed_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 25, 22, 10, 11, 253220)),
        ),
    ]
