from django.http import JsonResponse
from django.shortcuts import render

from .models import ExchangeRate, Cryptocurrency


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

def list_cryptocurrencies(request):
    cryptos = Cryptocurrency.objects.all()
    return render(request, 'currency-exchange/cryptos.html', {'cryptos': cryptos})

def buy_crypto(request, crypto_id):
    crypto = Cryptocurrency.objects.get(id=crypto_id)
    # For simplicity, let's assume the user buys 1 unit of the crypto
    usd_value = crypto.price_usd
    return render(request, 'currency-exchange/purchase_confirmation.html', {'crypto': crypto, 'usd_value': usd_value})