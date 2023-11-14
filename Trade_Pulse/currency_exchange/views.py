from django.http import JsonResponse
from django.shortcuts import render

from .models import ExchangeRate

def convert_btc_to_usd(request):
    context = {}
    if request.method == 'GET':
        btc_amount = request.GET.get('amount', None)
        if btc_amount:
            btc_amount = float(btc_amount)
            try:
                rate = ExchangeRate.objects.get(currency='BTC').rate
                context['usd_equivalent'] = btc_amount * rate
                context['btc_amount'] = btc_amount
            except ExchangeRate.DoesNotExist:
                context['error'] = 'Exchange rate not found'
    return render(request, 'currency-exchange/exchange.html', context)