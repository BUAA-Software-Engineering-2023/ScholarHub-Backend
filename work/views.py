import json
import os

from django.http.response import JsonResponse, StreamingHttpResponse

from favorite.models import Favorite, FavoriteItem
from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity, autocomplete
from utils.token import auth_check
from utils.upload import upload_file, upload_work
from work.models import Work, WorkStatus
from work.task import *
from urllib.parse import quote


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
    work_id = data.get('work_id')
    if not work_id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('work', work_id)
    if not success:
        return JsonResponse({
            'success': False,
            'message': result
        })

    if not result['open_access']['is_oa']:
        try:
            work = Work.objects.get(id=work_id, status=WorkStatus.ACCEPTED.value)
            result['open_access']['is_oa'] = True
            result['open_access']['oa_url'] = work.url(request)
        except Work.DoesNotExist:
            pass

    if request.user:
        try:
            history = History.objects.get(work=work_id, user=request.user)
        except History.DoesNotExist:
            title = result['title']
            celery_create_history.delay(title, work_id, request.user.id)
            return JsonResponse({
                'success': True,
                'data': result
            })
        history.save()
        for item in FavoriteItem.objects.filter(work=work_id):
            if item.favorite.user == request.user:
                result['is_like'] = True
                break
        if not result.get('is_like'):
            result['is_like'] = False
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['POST'])
@auth_check
def upload_work_view(request):
    id = request.POST.get('id')
    try:
        author = request.user.author
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': '您不是作者'
        })
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
    if result[0]['open_access']['is_oa']:
        return JsonResponse({
            'success': False,
            'message': '该作品已开放访问'
        })
    file = upload_work(request)
    if not file:
        return JsonResponse({
            'success': False,
            'message': '上传文件格式错误'
        })
    if Work.objects.filter(id=id).exists():
        work = Work.objects.get(id=id)
        if work.status == WorkStatus.ACCEPTED.value:
            return JsonResponse({
                'success': False,
                'message': '该作品已上传'
            })
        elif work.status == WorkStatus.REJECTED.value:
            work.path = file
            work.status = WorkStatus.PENDING.value
            work.save()
            return JsonResponse({
                'success': True,
                'message': '上传成功',
                'data': {
                    'id': work.id,
                    'title': work.title,
                    'name': work.name,
                    'url': work.url(request),
                    'status': WorkStatus.PENDING.info(),
                    'author': work.author.id
                }
            })
        elif work.status == WorkStatus.PENDING.value:
            return JsonResponse({
                'success': False,
                'message': '该作品正在审核中'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '该作品状态错误'
            })
    celery_create_work.delay(id, result[0]['title'], result[0]['display_name'], file, WorkStatus.PENDING.value,
                             author.id)
    return JsonResponse({
        'success': True,
        'message': '上传成功',
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
    if data.get('pass'):
        work.status = WorkStatus.ACCEPTED.value
        celery_create_message.delay(work.author.user.id, f'您的作品{work.title}已通过审核')
    else:
        work.status = WorkStatus.REJECTED.value
        celery_create_message.delay(work.author.user.id, f'您的作品{work.title}未通过审核')
    work.save()
    return JsonResponse({
        'success': True,
        'message': '审核成功',
        'data': {
            'id': work.id,
            'title': work.title,
            'name': work.name,
            'url': work.url(request),
            'status': WorkStatus.ACCEPTED.info(),
            'author': work.author.id
        }
    })


@request_methods(['GET'])
@auth_check
def mylist_work_view(request):
    try:
        author = request.user.author
    except AttributeError:
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
            'url': work.url(request),
            'status': WorkStatus(work.status).info(),
            'author': work.author.id
        })
    return JsonResponse({
        'success': True,
        'data': data
    })


@request_methods(['GET'])
@auth_check
def list_work_view(request):
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'message': '无权限'
        })
    works = Work.objects.filter(status=WorkStatus.PENDING.value)
    data = []
    for work in works:
        data.append({
            'id': work.id,
            'title': work.title,
            'name': work.name,
            'url': work.url(request),
            'status': WorkStatus(work.status).info(),
            'author': work.author.id
        })
    return JsonResponse({
        'success': True,
        'data': data
    })


@request_methods(['GET'])
def download_work_view(request):
    id = request.GET.get('id')
    print(id)
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
            'message': '不存在可供下载的论文'
        }, status=404)
    if work.status == WorkStatus.REJECTED.value:
        return JsonResponse({
            'success': False,
            'message': '不存在可供下载的论文'
        }, status=404)
    if work.status == WorkStatus.PENDING.value and (not request.user or not request.user.is_admin):
        return JsonResponse({
            'success': False,
            'message': '论文审核中，暂不支持下载'
        }, status=403)

    path = f'./files/{work.path}'

    if os.path.exists(path):
        response = StreamingHttpResponse(open(path, 'rb'),
                                         content_type='application/pdf')
        filename = work.title + '.pdf'
        response['Content-Disposition'] = f'inline;filename="{quote(filename)}"'
        return response
    else:
        return JsonResponse({
            'success': False,
            'message': '不存在可供下载的论文'
        }, status=404)


@request_methods(['GET'])
def autocomplete_view(request):
    search = request.GET.get('search')
    result = autocomplete('work', search)
    return JsonResponse({
        'success': True,
        'data': result
    })
