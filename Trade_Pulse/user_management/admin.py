from django.contrib import admin

from user_management.models import Wallet, Crypto, Purchase

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Crypto)
admin.site.register(Purchase)
