from ScholarHub.celery import app
from favorite.models import *


@app.task
def celery_create_favorite(user_id, title):
    favorite = Favorite(user_id=user_id, title=title)
    favorite.save()


@app.task
def celery_create_favorite_item(favorite_id, work, title):
    favorite_item = FavoriteItem(favorite_id=favorite_id, work=work, title=title)
    favorite_item.save()
