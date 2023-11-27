import json

from django.http import JsonResponse

from author.task import *
from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity, autocomplete, search_works_by_author_id
from utils.token import auth_check
from utils.upload import upload_file


@request_methods(['POST'])
def search_author_view(request):
    data = json.loads(request.body)
    result, success = search_entities_by_body('author', data)
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
def get_author_work_view(request):
    data = json.loads(request.body)
    author_id = data.get('author_id')
    page = data.get('page', 1)
    size = data.get('size', 25)
    if not author_id:
        return JsonResponse({
            'success': False,
            'message': '请给出作者id'
        })
    result = search_works_by_author_id(author_id, page, size)
    if result is None:
        return JsonResponse({
            'success': False,
            'message': '作者不存在'
        })
    return JsonResponse({
        'success': True,
        'data': result
    })

@request_methods(['POST'])
def author_detail_view(request):
    data = json.loads(request.body)
    author_id = data.get('author_id')
    if not author_id:
        return JsonResponse({
            'success': False,
            'message': '请给出id'
        })
    result, success = get_single_entity('author', author_id)
    if not success:
        return JsonResponse({
            'success': False,
            'message': result
        })
    author = Author.objects.filter(id=author_id).first()
    if author:
        result['profile'] = author.profile
        result['avatar'] = author.avatar
        result['display_name'] = author.name
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['POST'])
@auth_check
def apply_view(request):
    data = json.loads(request.body)
    author_id = data.get('author_id')
    if not author_id:
        return JsonResponse({
            'success': False,
            'message': '请给出认领的学者信息'
        })
    if Author.objects.filter(user=request.user).exists():
        return JsonResponse({
            'success': False,
            'message': '您已认领个人专属门户'
        })
    if Application.objects.filter(user=request.user, status=ApplicationStatus.PENDING.value).exists():
        return JsonResponse({
            'success': False,
            'message': '您已提交过申请,请耐心等待审核'
        })
    if Application.objects.filter(user=request.user, status=ApplicationStatus.ACCEPTED.value).exists():
        return JsonResponse({
            'success': False,
            'message': '您已通过审核,请不要重复提交申请'
        })
    celery_create_application.delay(request.user.id, ApplicationStatus.PENDING.value, author_id)
    return JsonResponse({
        'success': True,
        'message': '门户认证申请提交成功'
    })


@request_methods(['GET'])
@auth_check
def list_application_view(request):
    if request.user.is_admin:
        applications = Application.objects.all().order_by('-created_at')
    else:
        applications = Application.objects.filter(user=request.user).order_by('-created_at')
    result = []
    for application in applications:
        result.append({
            'application_id': application.id,
            'status': ApplicationStatus(application.status).info(),
            'created_at': application.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse({
        'success': True,
        'data': result
    })


@request_methods(['POST'])
@auth_check
def process_application_view(request):
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'message': '您不是管理员'
        }, status=403)
    data = json.loads(request.body)
    try:
        application = Application.objects.get(id=data.get('application_id'))
    except Application.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '不存在此申请'
        })
    if application.status != ApplicationStatus.PENDING.value:
        return JsonResponse({
            'success': False,
            'message': '此申请已处理'
        })
    if data.get('pass'):
        result = get_single_entity('author', application.author_id)
        celery_create_author.delay(id=application.author_id, user_id=application.user.id,
                                   name=result[0]['display_name'])
        celery_create_message.delay(application.user.id, '您的门户认证申请已通过')
        application.status = ApplicationStatus.ACCEPTED.value
        application.save()
        return JsonResponse({
            'success': True,
            'message': '申请批准成功',
            'data': {
                'application_id': application.id,
                'status': ApplicationStatus.ACCEPTED.info(),
            }
        })
    else:
        celery_create_message.delay(application.user.id, '您的门户认证申请未通过')
        application.status = ApplicationStatus.REJECTED.value
        application.save()
        return JsonResponse({
            'success': True,
            'message': '申请拒绝成功',
            'data': {
                'application_id': application.id,
                'status': ApplicationStatus.REJECTED.info(),
            }
        })


@request_methods(['PUT'])
@auth_check
def edit_author_view(request):
    data = json.loads(request.body)
    try:
        author = Author.objects.get(id=data.get('author_id'))
    except Author.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '不存在此作者'
        })
    if author.user != request.user:
        return JsonResponse({
            'success': False,
            'message': '您不是此作者'
        }, status=403)
    author.name = data.get('name', author.name)
    author.profile = data.get('profile', author.profile)
    author.avatar = data.get('avatar', author.avatar)
    author.save()
    return JsonResponse({
        'success': True,
        'data': {
            'author_id': author.id,
            'name': author.name,
            'profile': author.profile,
            'avatar': author.avatar
        }
    })


@request_methods(['POST'])
@auth_check
def upload_avatar_view(request):
    file = upload_file(request, 'image')
    if not file:
        return JsonResponse({
            'success': False,
            'message': '图片格式错误'
        })
    return JsonResponse({
        'success': True,
        "data": file
    })


@request_methods(['GET'])
def autocomplete_author_view(request):
    search = request.GET.get('search')
    result = autocomplete('author', search)
    return JsonResponse({
        'success': True,
        'data': result
    })
