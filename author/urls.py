from django.urls import path
from .views import *

urlpatterns = [
    path('author/search', search_author_view),
    path('author/author-detail', author_detail_view),
]
