from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    uuid = models.CharField(max_length=50, unique=True, default=0)
    symbol = models.CharField(max_length=10, default='BTS')
    name = models.CharField(max_length=255, default='Bitcoin')
    color = models.CharField(max_length=10, default='red')
    icon_url = models.URLField(default='https://cdn.coinranking.com/bOabBYkcX/bitcoin_btc.svg')
    market_cap = models.FloatField(default=0)
    price = models.FloatField(default=0)
    listed_at = models.DateTimeField(default=datetime.now())
    tier = models.IntegerField(default=0)
    change = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
    sparkline = models.JSONField(null=True)
    low_volume = models.BooleanField(default=False)
    # coinranking_url = models.URLField(default='user_management/bitcoin.png')
    volume_24hr = models.FloatField(default=0)
    btc_price = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=50)


class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)  # 'buy' or 'sell'
    transaction_date = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_photo = models.ImageField(upload_to='id_photos/', blank=True, null=True)
    # Add other profile-related fields


class Buyer(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    purchase_date = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return f"{self.user.username} - {self.currency.name}"
