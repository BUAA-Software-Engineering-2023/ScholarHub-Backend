from django.urls import path
from .views import *

urlpatterns = [
    path('work/search', search_works_view),
    path('work/detail', work_detail_view),
]