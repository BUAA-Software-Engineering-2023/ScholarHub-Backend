import json

from django.http import JsonResponse

from utils.decorator import request_methods
from utils.openalex import search_authors, get_single_author


@request_methods(['POST'])
def search_author_view(request):
    data = json.loads(request.body)
    search = data.get('search', '')
    filter = data.get('filter')
    sort = data.get('sort')
    page = int(data.get('page'))
    size = int(data.get('size'))
    result = search_authors(search, filter, sort, page, size)
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['POST'])
def author_detail_view(request):
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
    result = get_single_author(id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在此作者'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })
