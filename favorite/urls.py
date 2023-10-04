from django.urls import path
from .views import *

urlpatterns = [
    path('favorite', FavoriteView.as_view()),
    path('favoriteitem', FavoriteItemView.as_view()),
]
