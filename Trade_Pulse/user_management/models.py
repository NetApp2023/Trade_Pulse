from django.conf import settings
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id_photo = models.ImageField(upload_to='id_photos/', blank=True, null=True)
    # Add other profile-related fields


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Wallet with {self.amount} units"


class Crypto(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.DecimalField(max_digits=19, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} quantity of {self.crypto.name} bought at ${self.purchase_price} each"
