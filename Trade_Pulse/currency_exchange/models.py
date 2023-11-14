from django.db import models


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, default='BTC')
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.currency} to USD: {self.rate}"
