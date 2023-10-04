from django.http.response import JsonResponse

def request_methods(methods):
    """
    包装器，用于在调用视图函数前校验请求方法
    :param methods: 允许的请求方法
    :return:
    """
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse({
                    'success': False,
                    'message': '不允许的方法'
                })
            return func(request, *args, **kwargs)
        return wrap
    return decorator