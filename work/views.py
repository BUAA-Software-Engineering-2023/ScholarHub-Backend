import json

from django.http.response import JsonResponse
from utils.openalex import search_works, get_single_work

def search_works_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '不允许的方法'
        })
    data = json.loads(request.body)
    search = data.get('search', '')
    filter = data.get('filter')
    sort = data.get('sort')
    page = int(data.get('page', 1))
    size = int(data.get('size', 25))
    result = search_works(search, filter, sort, page, size)
    return JsonResponse({
        'success': True,
        'data': result
    })

def work_detail_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '不允许的方法'
        })
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_work(id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的论文'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })