import json

from django.http.response import JsonResponse

from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity
from utils.token import auth_check
from utils.upload import upload_file
from work.models import Work, WorkStatus


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


@request_methods(['POST'])
@auth_check
def upload_work_view(request):
    id = request.POST.get('id')
    author = request.user.author_set.first()
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出作品id'
        })
    result = get_single_entity('work', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的作品'
        })
    if result.open_access.is_oa:
        return JsonResponse({
            'success': False,
            'message': '该作品已开放访问'
        })
    file = upload_file(request, 'pdf')
    if not file:
        return JsonResponse({
            'success': False,
            'message': '上传文件格式错误'
        })
    work = Work(id=id, title=result.title, name=result.display_name, url=file, status=WorkStatus.PENDING.value,
                author=author)
    work.save()
    return JsonResponse({
        'success': True,
        'message': '上传成功',
        'data': {
            'id': work.id,
            'title': work.title,
            'name': work.name,
            'url': work.url,
            'status': WorkStatus.PENDING.info(),
            'author': work.author.id
        }
    })


@request_methods(['PATCH'])
@auth_check
def verify_work_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'message': '无权限'
        })
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出作品id'
        })
    try:
        work = Work.objects.get(id=id)
    except Work.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '不存在的作品'
        })
    work.status = WorkStatus.ACCEPTED.value
    work.save()
    return JsonResponse({
        'success': True,
        'message': '审核成功',
        'data': {
            'id': work.id,
            'title': work.title,
            'name': work.name,
            'url': work.url,
            'status': WorkStatus.ACCEPTED.info(),
            'author': work.author.id
        }
    })


@request_methods(['GET'])
@auth_check
def list_work_view(request):
    author = request.user.author
    if not author:
        return JsonResponse({
            'success': False,
            'message': '您不是作者'
        })
    works = author.work_set.all()
    data = []
    for work in works:
        data.append({
            'id': work.id,
            'title': work.title,
            'name': work.name,
            'url': work.url,
            'status': WorkStatus(work.status).info(),
            'author': work.author.id
        })
    return JsonResponse({
        'success': True,
        'data': data
    })


@request_methods(['POST'])
@auth_check
def download_work_view(request):
    data = json.loads(request.body)
    id = data.get('id')
    if not id:
        return JsonResponse({
            'success': False,
            'message': '请给出作品id'
        })
    result = get_single_entity('work', id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在的作品'
        })
    if result.open_access.is_oa:
        return JsonResponse({
            'success': True,
            'data': {
                'url': result.open_access.oa_url
            }
        })
    else:
        try:
            work = Work.objects.get(id=id)
        except Work.DoesNotExist:
            return JsonResponse({
                'success': True,
                'message': '该作品未开放访问'
            })
        return JsonResponse({
            'success': True,
            'data': {
                'url': work.url
            }
        })
