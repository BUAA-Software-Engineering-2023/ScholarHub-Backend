from ScholarHub.celery import app
from history.models import History
from message.models import Message
from work.models import Work


@app.task()
def celery_create_history(title, work_id, user_id):
    history = History.objects.filter(work=work_id, user=user_id)
    if history is None:
        history = History(title=title, work=work_id, user_id=user_id)
    history.save()


@app.task()
def celery_create_work(id, title, name, path, status, author_id):
    work = Work(id=id, title=title, name=name, path=path, status=status, author_id=author_id)
    work.save()


@app.task()
def celery_create_message(receiver_id, content):
    message = Message(receiver_id=receiver_id, content=content)
    message.save()
