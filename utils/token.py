import jwt
import time
from django.conf import settings
from django.http import JsonResponse

from user.models import User


def make_token(data: dict, expire: int = 30 * 24 * 3600) -> str:
    """
    根据给数据生成token

    :param data: token中存储的数据
    :param expire: token过期时间
    :return: 生成的token
    """
    key = settings.SECRET_KEY
    expire_at = time.time() + expire
    payload = {
        **data,
        'exp': expire_at
    }
    return jwt.encode(payload, key)


def parse_token(token):
    if not token:
        return None, 403
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None, 401
    try:
        user = User.objects.get(username=payload['username'])
    except User.DoesNotExist:
        return None, 401
    except Exception as e:
        print(f'意外报错：{e.args}')
        return None, 200
    return user, 200


def auth_check(func):
    """
    包装器，用于在调用函数前通过校验token判断是否登录
    :param func:
    :return:
    """

    def wrap(request, *args, **kwargs):
        if not request.user:
            if request.token_status == 403:
                return JsonResponse({
                    'success': False,
                    'message': '请先进行登录'
                }, status=403)
            if request.token_status == 401:
                return JsonResponse({
                    'success': False,
                    'message': '无效的token'
                })
            return JsonResponse({
                'success': False,
                'message': '未知错误'
            })
        return func(request, *args, **kwargs)

    return wrap


class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        request.user, request.token_status = parse_token(token)

        response = self.get_response(request)

        return response
