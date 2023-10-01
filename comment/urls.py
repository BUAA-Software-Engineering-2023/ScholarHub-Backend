from django.urls import path
from .views import *

urlpatterns = [
    path('comment/list', list_comment_view),
    path('comment/create', create_comment_view),
    path('comment/delete', delete_comment_view),
    path('comment/modify', modify_comment_view),
]
