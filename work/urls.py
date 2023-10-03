from django.urls import path
from .views import *

urlpatterns = [
    path('work/search', search_works_view),
    path('work/detail', work_detail_view),
    path('work/upload', upload_work_view),
    path('work/verify', verify_work_view),
    path('work/list', list_work_view),
    path('work/download', download_work_view),
]
