import json

from django.http.response import JsonResponse

from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity


@request_methods(['POST'])
def search_sources_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('source', data)
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def search_institutions_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('institution', data)
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def search_concepts_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('concept', data)
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def search_publishers_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('publisher', data)
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def search_funders_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('funder', data)
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['POST'])
def source_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_entity('source', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的来源'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def institution_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_entity('institution', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的机构'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def concept_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_entity('concept', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的话题'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def publisher_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_entity('publisher', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的出版社'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def funder_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result = get_single_entity('funder', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的基金会'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })