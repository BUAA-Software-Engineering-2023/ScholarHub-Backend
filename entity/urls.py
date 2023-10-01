from django.urls import path
from .views import *

urlpatterns = [
    path('source/search', search_sources_view),
    path('source/detail', source_detail_view),
    path('institution/search', search_institutions_view),
    path('institution/detail', institution_detail_view),
    path('concept/search', search_concepts_view),
    path('concept/detail', concept_detail_view),
    path('publisher/search', search_publishers_view),
    path('publisher/detail', publisher_detail_view),
    path('funder/search', search_funders_view),
    path('funder/detail', funder_detail_view)
]