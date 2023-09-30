from django.urls import path
from .views import *

urlpatterns = [
    path('author/search', search_author_view),
]
