import json
import random

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.http.response import JsonResponse
from django.template import loader
from django.core.mail import EmailMessage

from user.models import User
from utils.cache import get_verification_code_cache, set_verification_code_cache
from utils.token import make_token


def send_verification_code_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '不允许的请求方法'
        })

    data = json.loads(request.body)
    email = data.get('email')
    try:
        email_validator = EmailValidator()
        email_validator(email)
    except ValidationError:
        return JsonResponse({
            'success': False,
            'message': '邮箱格式错误'
        })

    code = str(random.randrange(100000, 999999))

    # 写入缓存
    set_verification_code_cache(email, code)

    # TODO 使用celery处理发送邮件
    t = loader.get_template('verification_code.html')
    html = t.render({'code': code})
    # 发送邮件
    msg = EmailMessage('ScholarHub邮箱验证码', html,
                       to=[email])
    msg.content_subtype = 'html'
    send_status = msg.send()
    if not send_status:
        return JsonResponse({
            'success': False,
            'message': '验证码发送失败，请稍后重试'
        })
    # TODO 最终需移除返回的验证码
    return JsonResponse({
        'success': True,
        'code': code
    })


def register_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '不允许的请求方法'
        })

    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not username or not email or code or not password:
        return JsonResponse({
            'success': False,
            'message': '用户名、邮箱、验证码、密码不能为空'
        })

    try:
        email_validator = EmailValidator()
        email_validator(email)
    except ValidationError:
        return JsonResponse({
            'success': False,
            'message': '邮箱格式错误'
        })

    if password != confirm_password:
        return JsonResponse({
            'success': False,
            'message': '两次密码不一致'
        })

    if code != get_verification_code_cache(email):
        return JsonResponse({
            'success': False,
            'message': '验证码错误'
        })

    try:
        User.objects.get(username=username)
        return JsonResponse({
            'success': False,
            'message': '用户名已被注册'
        })
    except User.DoesNotExist:
        pass

    try:
        User.objects.get(email=email)
        return JsonResponse({
            'success': False,
            'message': '邮箱已被注册'
        })
    except User.DoesNotExist:
        pass

    encrypted_password = make_password(password)
    user = User(username=username, email=email, password=encrypted_password)
    try:
        validate_password(password, user)
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': e.message.messages()[0].message
        })
    user.save()
    return JsonResponse({
        'success': True
    })


def login_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '不允许的请求方法'
        })

    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return JsonResponse({
            'success': False,
            'message': '用户名或密码不能为空'
        })

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '用户名或密码错误'
        })

    if not check_password(password, user.password):
        return JsonResponse({
            'success': False,
            'message': '用户名或密码错误'
        })

    token = make_token({'id': user.id})
    return JsonResponse({
        'success': True,
        'data': {
            'token': token
        }
    })
