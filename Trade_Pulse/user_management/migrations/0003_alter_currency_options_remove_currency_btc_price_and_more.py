# Generated by Django 4.2.5 on 2023-11-26 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_cryptocurrency_market_cap_cryptocurrency_volume_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currency',
            options={'verbose_name_plural': 'currencies'},
        ),
        migrations.RemoveField(
            model_name='currency',
            name='btc_price',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='change',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='color',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='icon_url',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='listed_at',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='low_volume',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='market_cap',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='name',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='price',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='rank',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='sparkline',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='tier',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='volume_24hr',
        ),
        migrations.AddField(
            model_name='currency',
            name='code',
            field=models.CharField(default=1, help_text="Currency ISO code (e.g., 'USD', 'EUR')", max_length=3, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='currency',
            name='flag',
            field=models.ImageField(default=1, help_text="Image of the country's flag", upload_to='flags/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='currency',
            name='rate_to_usd',
            field=models.DecimalField(decimal_places=4, default=1, help_text='Conversion rate to USD', max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(help_text="Currency symbol (e.g., '$', '€')", max_length=10),
        ),
    ]
