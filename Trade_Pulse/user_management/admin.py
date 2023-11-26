from django.contrib import admin

from user_management.models import Cryptocurrency, ExchangeRate, CryptoPriceHistory, Purchase, Currency

# Register your models here.
admin.site.register(Cryptocurrency)
admin.site.register(Currency)
admin.site.register(ExchangeRate)
admin.site.register(CryptoPriceHistory)
admin.site.register(Purchase)