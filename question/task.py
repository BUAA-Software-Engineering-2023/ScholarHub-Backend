from ScholarHub.celery import app
from message.models import Message
from question.models import *


@app.task()
def celery_create_question(work_id, title, content, asker_id):
    question = Question(work=work_id, title=title, content=content, asker_id=asker_id)
    question.save()


@app.task()
def celery_create_answer(question_id, content, answerer_id):
    answer = Answer(question_id=question_id, content=content, answerer_id=answerer_id)
    answer.save()


@app.task()
def celery_create_message(receiver_id, content):
    message = Message(receiver_id=receiver_id, content=content)
    message.save()
