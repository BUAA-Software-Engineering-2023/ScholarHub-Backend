import json

from django.http.response import JsonResponse

from utils.decorator import request_methods
from utils.openalex import *


@request_methods(['POST'])
def search_sources_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('source', data)
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
def search_institutions_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('institution', data)
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
def search_concepts_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('concept', data)
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
def search_publishers_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('publisher', data)
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
def search_funders_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('funder', data)
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
def source_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('source', id)
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
def institution_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('institution', id)
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
def concept_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('concept', id)
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
def publisher_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('publisher', id)
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
def funder_detail_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('funder', id)
    if not success:
        return JsonResponse({
            'success': False,
            'message': result
        })
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['GET'])
def get_total_numbers_view(request):
    result = get_entities_numbers()
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['GET'])
def get_recommendations_view(request):
    result = None
    if request.user:
        history = request.user.history_set.all().order_by('-updated_at')
        temp = []
        for h in history:
            temp.append(h.work)
        result = get_recommendations(temp)
    if not result:
        # 没有相关论文时，获取引用量最高的10篇
        result, success = search_entities_by_body('work', {
            'size': 10,
            'sort': {
                'cited_by_count': 'desc'
            }
        })
        if not success:
            JsonResponse({
                'success': False,
                'message': "获取openalex数据失败"
            })
        result = result.result
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['GET'])
def autocomplete_source_view(request):
    search = request.GET.get('search')
    result = autocomplete('source', search)
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['GET'])
def autocomplete_institution_view(request):
    search = request.GET.get('search')
    result = autocomplete('institution', search)
    return (JsonResponse({
        'success': True,
        'data': result
    }))


@request_methods(['GET'])
def autocomplete_concept_view(request):
    search = request.GET.get('search')
    result = autocomplete('concept', search)
    return (JsonResponse({
        'success': True,
        'data': result
    }))


@request_methods(['GET'])
def autocomplete_publisher_view(request):
    search = request.GET.get('search')
    result = autocomplete('publisher', search)
    return (JsonResponse({
        'success': True,
        'data': result
    }))


@request_methods(['GET'])
def autocomplete_funder_view(request):
    search = request.GET.get('search')
    result = autocomplete('funder', search)
    return (JsonResponse({
        'success': True,
        'data': result
    }))
