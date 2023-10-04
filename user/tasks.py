from django.core.mail import EmailMessage
from django.template import loader

from ScholarHub.celery import app
from user.models import User


@app.task()
def celery_send_verification_code(email, code):
    t = loader.get_template('verification_code.html')
    html = t.render({'code': code})
    # 发送邮件
    msg = EmailMessage('ScholarHub邮箱验证码', html,
                       to=[email])
    msg.content_subtype = 'html'
    msg.send()


@app.task()
def celery_create_user(username, email, encrypted_password):
    user = User(username=username, email=email, password=encrypted_password)
    user.save()
