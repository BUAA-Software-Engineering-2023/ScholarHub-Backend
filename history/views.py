import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from history.models import History
from utils.cache import clear_openalex_histories_details_cache
from utils.openalex import get_histories_details
from utils.token import auth_check


# Create your views here.

class HistoryView(View):
    @method_decorator(auth_check)
    def get(self, request):
        user = request.user
        history = user.history_set.all().order_by('-updated_at')
        if not history:
            return JsonResponse({
                'success': True,
                'data': []
            })
        result = []
        works = [h.work for h in history]
        histories_details = get_histories_details(works, user.id)
        for h in history:
            history_detail = histories_details.get(h.work)
            result.append({
                'id': h.id,
                'title': h.title,
                'work': h.work,
                'updated_at': h.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'display_name': history_detail.get('display_name', ''),
                'publication_year': history_detail.get('publication_year', ''),
                'type': history_detail.get('type', ''),
                'authorships': history_detail.get('authorships', []),
                'concepts': history_detail.get('concepts', []),
                'cited_by_count': history_detail.get('cited_by_count', 0),
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
        clear_openalex_histories_details_cache(request.user.id)
        return JsonResponse({
            'success': True,
            'message': '删除成功'
        })
