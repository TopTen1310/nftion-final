from django.urls import path
from .views import log_out, check_credentials
app_name = 'auth_app'


urlpatterns = [
    path('logout/', log_out, name='logout'),
    path('change_email/', check_credentials, name='change_email')
]
