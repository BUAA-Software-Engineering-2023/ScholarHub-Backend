from ScholarHub.celery import app
from django.template import loader
from django.core.mail import EmailMessage


@app.task()
def celery_send_verification_code(email, code):
    print(email, code)
    t = loader.get_template('verification_code.html')
    html = t.render({'code': code})
    # 发送邮件
    msg = EmailMessage('ScholarHub邮箱验证码', html,
                       to=[email])
    msg.content_subtype = 'html'
    msg.send()
