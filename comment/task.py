from ScholarHub.celery import app
from comment.models import *


@app.task()
def celery_create_comment(work, sender_id, content, reply_id=None):
    comment = Comment(work=work, sender_id=sender_id, content=content, reply_id=reply_id)
    comment.save()
