from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import home,registration,login_view,logout_view, forgot_password

urlpatterns = [
    path('', home, name='home'),
    path('register/', registration, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    # path('password_reset/', include('django.contrib.auth.urls')),
    # Add other URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)