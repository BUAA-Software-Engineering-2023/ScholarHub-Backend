import json

from django.http.response import JsonResponse

from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity


@request_methods(['POST'])
def search_works_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('work', data)
    if not success:
        return JsonResponse({
            'success': False,
            'message': result
        })
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
    result, success = get_single_entity('work', id)
    if not success:
        return JsonResponse({
            'success': False,
            'message': result
        })
    return JsonResponse({
        'success': True,
        'data': result
    })
