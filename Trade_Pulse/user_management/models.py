from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    exchange_rate = models.FloatField()


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
