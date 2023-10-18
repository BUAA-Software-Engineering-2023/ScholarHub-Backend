from django.urls import path
from .views import *

urlpatterns = [
    path('author/search', search_author_view),
    path('author/detail', author_detail_view),
    path('author/apply', apply_view),
    path('author/list-application', list_application_view),
    path('author/process-application', process_application_view),
    path('author/edit', edit_author_view),
    path('author/avatar', upload_avatar_view),
    path('author/autocomplete', autocomplete_author_view)
]
