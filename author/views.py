import json

from django.http import JsonResponse

from utils.decorator import request_methods
from utils.openalex import search_authors


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
