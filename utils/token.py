import jwt
import time
from django.conf import settings
from django.http import JsonResponse

from user.models import User


def make_token(data:dict, expire:int=30*24*3600)->str:
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

def auth_check(func):
    """
    包装器，用于在调用函数前通过校验token判断是否登录
    :param func:
    :return:
    """
    def wrap(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return JsonResponse({
                'success': False,
                'message': '请先进行登录'
            }, status=403)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        except jwt.DecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的token'
            }, status=401)
        try:
            user = User.objects.get(username=payload['username'])
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '无效的token'
            }, status=401)
        except Exception as e:
            print(f'意外报错：{e.args}')
            return JsonResponse({
                'success': False,
                'message': '未知错误'
            })
        request.user = user
        return func(request, *args, **kwargs)
    return wrap