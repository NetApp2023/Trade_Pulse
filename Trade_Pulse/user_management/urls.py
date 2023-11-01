from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import home,registration,login_view,logout_view, CustomPasswordResetView

urlpatterns = [
    path('', home, name='home'),
    path('register/', registration, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot_password/', CustomPasswordResetView.as_view(), name='forgot_password'),
    # Add other URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)