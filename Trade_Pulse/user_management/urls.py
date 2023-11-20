from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import home, registration, login_view, logout_view, base, add_money, buy_crypto, sell_crypto

urlpatterns = [
    path('', home, name='home'),
    path('register/', registration, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('addmoney', add_money, name='add_money'),
    path('buy_crypto/<int:crypto_id>', buy_crypto, name='buy_crypto'),
    path('sell_crypto/<int:crypto_id>', sell_crypto, name='sell_crypto')
    # Add other URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)