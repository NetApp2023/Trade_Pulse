from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views


urlpatterns = [
    path('cryptos', views.list_cryptocurrencies, name='list_cryptocurrencies'),
    path('buy_crypto/<int:crypto_id>/', views.buy_crypto, name='buy_crypto'),
    path('currency-exchange', views.convert_btc_to_usd, name='convert_btc_to_usd'),
    # Add other URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)