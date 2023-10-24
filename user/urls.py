from django.urls import path
from .views import *

urlpatterns = [
    path('send-code', send_verification_code_view),
    path('register', register_view),
    path('login', login_view),
    path('user/update_email', update_email_view),
    path('user/update_password', update_password_view),
    path('user/update', update_userinfo_view),
    path('user/retrieve', retrieve_password_view),
    path('user/info', get_userinfo_view),
    path('user/upload', upload_avatar_view),
]
