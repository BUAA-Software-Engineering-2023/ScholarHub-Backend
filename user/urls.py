from django.urls import path
from .views import *

urlpatterns = [
    path('send-code', send_verification_code_view),
    path('register', register_view)
]