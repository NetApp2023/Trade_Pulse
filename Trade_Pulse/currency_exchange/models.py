from django.db import models


class Cryptocurrency(models.Model):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='cryptocurrency_logos/')
    price_usd = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.logo})"

class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, default='BTC')
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.currency} to USD: {self.rate}"
