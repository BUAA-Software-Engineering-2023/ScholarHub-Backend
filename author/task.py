from ScholarHub.celery import app
from author.models import *
from message.models import Message


@app.task()
def celery_create_application(user_id, status, author_id):
    application = Application(status=status, user_id=user_id, author_id=author_id)
    application.save()


@app.task()
def celery_create_author(id, user_id, name):
    author = Author(id=id, user_id=user_id, name=name)
    author.save()


@app.task()
def celery_create_message(receiver_id, content):
    message = Message(receiver_id=receiver_id, content=content)
    message.save()
