from django.urls import path
from .views import *

urlpatterns = [
    path('message/read', read_message_view),
    path('message', MessageView.as_view()),
]
