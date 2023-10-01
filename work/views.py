import json

from django.http.response import JsonResponse

from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity


@request_methods(['POST'])
def search_works_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('work', data)
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def work_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_entity('work', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的论文'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })
