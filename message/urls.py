from django.urls import path
from .views import *

urlpatterns = [
    path('message', MessageView.as_view()),
    path('message/read', read_message_view),
]
