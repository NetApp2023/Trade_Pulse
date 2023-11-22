from django.contrib import admin

from user_management.models import Cryptocurrency, ExchangeRate, CryptoPriceHistory

# Register your models here.
admin.site.register(Cryptocurrency)
admin.site.register(ExchangeRate)
admin.site.register(CryptoPriceHistory)