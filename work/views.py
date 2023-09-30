import json

from django.http.response import JsonResponse
from utils.openalex import search_works

def search_work_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '不允许的方法'
        })
    data = json.loads(request.body)
    search = data.get('search', '')
    filter = data.get('filter')
    sort = data.get('sort')
    page = int(data.get('page'))
    size = int(data.get('size'))
    result = search_works(search, filter, sort, page, size)
    return JsonResponse({
        'success': True,
        'data': result
    })