import json
import random

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.http.response import JsonResponse

from user.models import User
from utils.cache import get_verification_code_cache, set_verification_code_cache, delete_verification_code_cache
from utils.decorator import request_methods
from utils.token import make_token, auth_check
from utils.upload import upload_file
from .tasks import celery_send_verification_code, celery_create_user


@request_methods(['POST'])
def send_verification_code_view(request):
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

    celery_send_verification_code.delay(email, code)

    return JsonResponse({
        'success': True,
        'message': '发送成功'
    })


@request_methods(['POST'])
def register_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not username or not email or not code or not password:
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
            'message': e.messages[0]
        })
    celery_create_user.delay(username, email, encrypted_password)
    delete_verification_code_cache(email)
    return JsonResponse({
        'success': True
    })


@request_methods(['POST'])
def login_view(request):
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

    token = make_token({'id': user.id, 'username': user.username})
    delete_verification_code_cache(user.email)
    try:
        author = user.author
    except AttributeError:
        author = None
    return JsonResponse({
        'success': True,
        'data': {
            'token': token,
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar if user.avatar else "https://img.zcool.cn/community/0177b355ed01bc6ac7251df8f6be5a.png",
            'email': user.email,
            'is_admin': user.is_admin,
            'is_author': author is not None,
            'author_id': author.id if author else None
        }
    })


@request_methods(['GET'])
@auth_check
def get_userinfo_view(request):
    user = request.user
    try:
        author = user.author
    except AttributeError:
        author = None
    return JsonResponse({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar if user.avatar else "https://img.zcool.cn/community/0177b355ed01bc6ac7251df8f6be5a.png",
            'email': user.email,
            'is_admin': user.is_admin,
            'is_author': author is not None,
            'author_id': author.id if author else None
        }
    })


@request_methods(['PUT'])
@auth_check
def update_userinfo_view(request):
    user = request.user
    data = json.loads(request.body)
    nickname = data.get('nickname', user.nickname)
    avatar = data.get('avatar', "https://img.zcool.cn/community/0177b355ed01bc6ac7251df8f6be5a.png")
    user.nickname = nickname
    user.avatar = avatar
    user.save()
    return JsonResponse({
        'success': True,
        'message': '修改成功'
    })


@request_methods(['PUT'])
@auth_check
def update_email_view(request):
    user = request.user
    data = json.loads(request.body)
    email = data.get('email', user.email)
    code = data.get('code')
    if email != user.email:
        try:
            email_validator = EmailValidator()
            email_validator(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': '邮箱格式错误'
            })
        try:
            User.objects.get(email=email)
            return JsonResponse({
                'success': False,
                'message': '邮箱已被注册'
            })
        except User.DoesNotExist:
            pass
        if code != get_verification_code_cache(email):
            return JsonResponse({
                'success': False,
                'message': '验证码错误'
            })
        user.email = email
        return JsonResponse({
            'success': True,
            'message': '修改成功'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '新邮箱地址不能与旧邮箱相同'
        })


@request_methods(['PUT'])
@auth_check
def update_password_view(request):
    user = request.user
    data = json.loads(request.body)
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not old_password or not new_password:
        return JsonResponse({
            'success': False,
            'message': '旧密码或新密码不能为空'
        })
    if not check_password(old_password, user.password):
        return JsonResponse({
            'success': False,
            'message': '原密码错误'
        })
    if old_password == new_password:
        return JsonResponse({
            'success': False,
            'message': '新旧密码不能相同'
        })
    user.password = make_password(new_password)
    user.save()
    return JsonResponse({
        'success': True,
        'message': '修改成功'
    })


@request_methods(['PUT'])
@auth_check
def retrieve_password_view(request):
    user = request.user
    data = json.loads(request.body)
    code = data.get('code')
    new_password = data.get('new_password')
    if not code or not new_password:
        return JsonResponse({
            'success': False,
            'message': '验证码或密码不能为空'
        })
    if code != get_verification_code_cache(user.email):
        return JsonResponse({
            'success': False,
            'message': '验证码错误'
        })
    user.password = make_password(new_password)
    user.save()
    return JsonResponse({
        'success': True,
        'message': '修改成功'
    })


@request_methods(['POST'])
@auth_check
def upload_avatar_view(request):
    file = upload_file(request, 'image')
    if not file:
        return JsonResponse({
            'success': False,
            'message': '图片格式错误'
        })
    return JsonResponse({
        'success': True,
        "data": file
    })
