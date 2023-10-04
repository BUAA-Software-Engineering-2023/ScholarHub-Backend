from ScholarHub.celery import app
from comment.models import *
from message.models import *


@app.task()
def celery_create_comment(work, sender_id, content, reply_id=None):
    comment = Comment(work=work, sender_id=sender_id, content=content, reply_id=reply_id)
    comment.save()


@app.task()
def celery_create_message(receiver_id, content):
    message = Message(receiver_id=receiver_id, content=content)
    message.save()
