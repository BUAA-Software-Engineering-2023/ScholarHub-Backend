from django.urls import path
from .views import *

urlpatterns = [
    path('history', HistoryView.as_view()),
]
