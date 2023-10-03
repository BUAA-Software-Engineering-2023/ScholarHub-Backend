import json

from django.http import JsonResponse

from author.models import Author, Application, ApplicationStatus
from utils.decorator import request_methods
from utils.openalex import search_entities_by_body, get_single_entity
from utils.token import auth_check
from utils.upload import upload_file


@request_methods(['POST'])
def search_author_view(request):
    data = json.loads(request.body)
    result = search_entities_by_body('author', data)
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
    result = get_single_entity('author', author_id)
    if not result:
        return JsonResponse({
            'success': False,
            'message': '不存在此作者'
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
    application = Application.objects.create(user=request.user, status=ApplicationStatus.PENDING.value,
                                             author_id=author_id)
    return JsonResponse({
        'success': True,
        'data': {
            'application_id': application.id,
            'status': ApplicationStatus.PENDING.info(),
            'author_id': author_id
        }
    })


@request_methods(['GET'])
@auth_check
def list_application_view(request):
    if request.user.is_admin:
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(user=request.user)
    result = []
    for application in applications:
        result.append({
            'application_id': application.id,
            'status': ApplicationStatus(application.status).info(),
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
        application.status = ApplicationStatus.ACCEPTED.value
        application.save()
        result = get_single_entity(application.author_id)
        author = Author.objects.create(id=application.author_id, user=application.user, name=result.get('display_name'))
        return JsonResponse({
            'success': True,
            'data': {
                'application_id': application.id,
                'status': ApplicationStatus.ACCEPTED.info(),
                'author_id': author.id,
                'author_name': author.name
            }
        })
    else:
        application.status = ApplicationStatus.REJECTED.value
        application.save()
        return JsonResponse({
            'success': True,
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
