from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import home,registration,login_view,logout_view, forgot_password,coin_details, user_profile, payment_view, payment_success

urlpatterns = [
    path('', home, name='home'),
    path('register/', registration, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('coin_details/<str:coin_id>/', coin_details, name='coin_details'),
    path('user_profile/', user_profile, name='user_profile'),
    path('payment/', payment_view, name='payment_view'),
    path('payment/success/', payment_success, name='payment_success'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)