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
    def get(self, request):
        user = request.user
        history = user.history_set.all().order_by('-updated_at')
        result = []
        for h in history:
            result.append({
                'id': h.id,
                'title': h.title,
                'work': h.work,
                'updated_at': h.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return JsonResponse({
            'success': True,
            'data': result
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
