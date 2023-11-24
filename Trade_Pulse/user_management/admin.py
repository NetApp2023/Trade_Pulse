from django.contrib import admin

from user_management.models import Cryptocurrency, ExchangeRate, CryptoPriceHistory, Purchase

# Register your models here.
admin.site.register(Cryptocurrency)
admin.site.register(ExchangeRate)
admin.site.register(CryptoPriceHistory)
admin.site.register(Purchase)