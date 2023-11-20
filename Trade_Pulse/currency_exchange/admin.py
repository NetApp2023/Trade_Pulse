from django.contrib import admin

from currency_exchange.models import Cryptocurrency, ExchangeRate

# Register your models here.
admin.site.register(Cryptocurrency)
admin.site.register(ExchangeRate)