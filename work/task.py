from ScholarHub.celery import app
from history.models import History
from work.models import Work


@app.task()
def celery_create_history(title, work_id, user_id):
    history = History(title=title, work=work_id, user_id=user_id)
    history.save()


@app.task()
def celery_create_work(id, title, name, url, status, author_id):
    work = Work(id=id, title=title, name=name, url=url, status=status, author_id=author_id)
    work.save()
