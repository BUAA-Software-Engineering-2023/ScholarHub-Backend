import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from utils.openalex import get_single_entity
from utils.token import auth_check
from .task import *


# Create your views here.


class FavoriteView(View):
    @method_decorator(auth_check)
    def get(self, request):
        user = request.user
        favorites = user.favorite_set.all().order_by('-created_at')
        return JsonResponse({
            'success': True,
            'data': [favorite.info() for favorite in favorites],
        })

    @method_decorator(auth_check)
    def post(self, request):
        data = json.loads(request.body)
        user = request.user
        title = data.get('title')
        if not title:
            return JsonResponse({
                'success': False,
                'message': '请输入标题',
            })
        celery_create_favorite.delay(user.id, title)
        return JsonResponse({
            'success': True,
            'message': '创建成功',
        })

    @method_decorator(auth_check)
    def delete(self, request):
        data = json.loads(request.body)
        favorite_id = data.get('favorite_id')
        if not favorite_id:
            return JsonResponse({
                'success': False,
                'message': '请输入收藏夹id',
            })
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '收藏夹不存在',
            })
        favorite.delete()
        return JsonResponse({
            'success': True,
            'message': '删除成功',
        })

    @method_decorator(auth_check)
    def put(self, request):
        data = json.loads(request.body)
        favorite_id = data.get('favorite_id')
        title = data.get('title')
        if not favorite_id:
            return JsonResponse({
                'success': False,
                'message': '请输入收藏夹id',
            })
        if not title:
            return JsonResponse({
                'success': False,
                'message': '请输入标题',
            })
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '收藏夹不存在',
            })
        favorite.title = title
        favorite.save()
        return JsonResponse({
            'success': True,
            'message': '修改成功',
        })


class FavoriteItemView(View):
    @method_decorator(auth_check)
    def post(self, request):
        data = json.loads(request.body)
        favorite_id = data.get('favorite_id')
        work = data.get('work_id')
        if not favorite_id:
            return JsonResponse({
                'success': False,
                'message': '请输入收藏夹id',
            })
        if not work:
            return JsonResponse({
                'success': False,
                'message': '请输入作品id',
            })
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '收藏夹不存在',
            })
        try:
            FavoriteItem.objects.get(favorite=favorite, work=work)
        except FavoriteItem.DoesNotExist:
            result, success = get_single_entity('work', work)
            if not success:
                return JsonResponse({
                    'success': False,
                    'message': '作品不存在',
                })
            celery_create_favorite_item.delay(favorite.id, work, result['title'])
            return JsonResponse({
                'success': True,
                'message': '创建成功',
            })
        return JsonResponse({
            'success': False,
            'message': '该作品已收藏',
        })

    @method_decorator(auth_check)
    def delete(self, request):
        data = json.loads(request.body)
        favorite_item_id = data.get('favorite_item_id')
        if not favorite_item_id:
            return JsonResponse({
                'success': False,
                'message': '请输入收藏id',
            })
        try:
            favorite_item = FavoriteItem.objects.get(id=favorite_item_id)
        except FavoriteItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '收藏不存在',
            })
        favorite_item.delete()
        return JsonResponse({
            'success': True,
            'message': '删除成功',
        })

    @method_decorator(auth_check)
    def get(self, request):
        favorite_id = request.GET.get('favorite_id')
        if not favorite_id:
            return JsonResponse({
                'success': False,
                'message': '请输入收藏夹id',
            })
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '收藏夹不存在',
            })
        return JsonResponse({
            'success': True,
            'data': favorite.info(),
        })
