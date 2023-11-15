from django.contrib import admin
from django.db import models
from .models import Currency, Buyer, UserProfile, Payment,PaymentHistory

# Register your models here.
admin.site.register(Currency)
admin.site.register(Buyer)
admin.site.register(UserProfile)
admin.site.register(Payment)
admin.site.register(PaymentHistory)

