from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import home, registration, login_view, logout_view, forgot_password, coin_details, buy_crypto, \
    crypto_detail, add_money, sell_crypto, Payment_History, base

urlpatterns = [
    path('', base, name='base'),
    path('home/', home, name='home'),
    path('register/', registration, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('coin_details/<str:coin_id>/', coin_details, name='coin_details'),
    path('buy_crypto/<int:crypto_id>/', buy_crypto, name='buy_crypto'),
    path('crypto_detail/<str:crypto_name>/', crypto_detail, name='crypto_detail'),
    path('addmoney', add_money, name='add_money'),
    path('buy_crypto/<int:crypto_id>', buy_crypto, name='buy_crypto'),
    path('sell_crypto/<int:crypto_id>', sell_crypto, name='sell_crypto'),
    path('Payment_History/', Payment_History, name='Payment_History')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)