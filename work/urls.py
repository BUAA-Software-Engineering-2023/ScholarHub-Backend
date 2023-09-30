from django.urls import path
from .views import *

urlpatterns = [
    path('work/search', search_work_view),
]