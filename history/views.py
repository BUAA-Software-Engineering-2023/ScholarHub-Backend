import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from history.models import History
from utils.openalex import get_single_entity
from utils.token import auth_check


# Create your views here.

class HistoryView(View):
    @method_decorator(auth_check)
    def post(self, request):
        data = json.loads(request.body)
        work_id = data.get('work_id')
        if not work_id:
            return JsonResponse({
                'success': False,
                'message': '请给出work_id'
            })
        result = get_single_entity('work', work_id)
        if not result:
            return JsonResponse({
                'success': False,
                'message': '该作品不存在'
            })
        try:
            history = History.objects.get(work=work_id, user=request.user)
        except History.DoesNotExist:
            title = result[0]['title']
            history = History(title=title, work=work_id, user=request.user)
            history.save()
            return JsonResponse({
                'success': True,
                'message': '添加成功',
                'data': {
                    'id': history.id,
                    'title': title,
                    'work': work_id,
                    'updated_at': history.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })
        history.save()
        return JsonResponse({
            'success': True,
            'message': '更新成功',
            'data': {
                'id': history.id,
                'title': history.title,
                'work': history.work,
                'updated_at': history.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })

    @method_decorator(auth_check)
    def delete(self, request):
        data = json.loads(request.body)
        history_id = data.get('history_id')
        try:
            history = History.objects.get(id=history_id)
        except History.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'history_id不存在'
            })
        history.delete()
        return JsonResponse({
            'success': True,
            'message': '删除成功'
        })
