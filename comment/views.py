import json

from django.http import JsonResponse

from comment.task import *
from utils.decorator import request_methods
from utils.token import auth_check
from utils.upload import upload_file


# Create your views here.

@request_methods(['POST'])
def list_comment_view(request):
    data = json.loads(request.body)
    work_id = data.get('work_id')
    reverse = data.get('reverse')
    if not work_id:
        return JsonResponse({
            'success': False,
            'message': '请提供学术成果信息'
        })
    if reverse or reverse is None:
        comments = Comment.objects.filter(work=work_id).order_by('-is_top', '-created_at')
    else:
        comments = Comment.objects.filter(work=work_id).order_by('-is_top', 'created_at')
    comments = [comment.info() for comment in comments]
    return JsonResponse({
        'success': True,
        'data': comments
    })


@request_methods(['POST'])
@auth_check
def create_comment_view(request):
    data = json.loads(request.body)
    work_id = data.get('work_id')
    content = data.get('content')
    reply_id = data.get('reply_id')
    if not work_id:
        return JsonResponse({
            'success': False,
            'message': '请提供学术成果信息'
        })
    if not content:
        return JsonResponse({
            'success': False,
            'message': '请提供评论内容'
        })
    if reply_id:
        try:
            reply = Comment.objects.get(id=reply_id)
        except Comment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '回复评论不存在'
            })
        celery_create_comment.delay(work_id, request.user.id, content, reply_id)
        celery_create_message.delay(reply.sender.id, f'您的评论有了来自{request.user.nickname}的新回复')
        return JsonResponse({
            'success': True,
            'message': '回复评论成功',
        })
    else:
        celery_create_comment.delay(work_id, request.user.id, content)
        return JsonResponse({
            'success': True,
            'message': '评论成功',
        })


@request_methods(['DELETE'])
@auth_check
def delete_comment_view(request):
    user = request.user
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    if not comment_id:
        return JsonResponse({
            'success': False,
            'message': '请提供评论信息'
        })
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '评论不存在'
        })
    if user.is_admin or comment.sender == request.user:
        comment.delete()
        return JsonResponse({
            'success': True,
            'message': '删除评论成功'
        })
    else:
        if comment.sender != user:
            return JsonResponse({
                'success': False,
                'message': '无权限删除评论'
            })
        comment.delete()
        return JsonResponse({
            'success': True,
            'message': '删除评论成功'
        })


@request_methods(['PATCH'])
@auth_check
def modify_comment_view(request):
    user = request.user
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    content = data.get('content')
    if not comment_id:
        return JsonResponse({
            'success': False,
            'message': '请提供评论信息'
        })
    if not content:
        return JsonResponse({
            'success': False,
            'message': '请提供评论内容'
        })
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '评论不存在'
        })
    if comment.sender != user:
        return JsonResponse({
            'success': False,
            'message': '无权限修改评论'
        })
    comment.content = content
    comment.save()
    return JsonResponse({
        'success': True,
        'message': '修改评论成功',
        'data': comment.info()
    })


@request_methods(['POST'])
@auth_check
def upload_image_view(request):
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


@request_methods(['PATCH'])
@auth_check
def top_comment_view(request):
    user = request.user
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    if not comment_id:
        return JsonResponse({
            'success': False,
            'message': '请提供评论信息'
        })
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '评论不存在'
        })
    if comment.reply:
        return JsonResponse({
            'success': False,
            'message': '回复评论无法置顶'
        })
    if user.is_admin:
        comment.is_top = True
        comment.save()
        return JsonResponse({
            'success': True,
            'message': '置顶评论成功'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '无权限置顶评论'
        })


@request_methods(['PATCH'])
@auth_check
def untop_comment_view(request):
    user = request.user
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    if not comment_id:
        return JsonResponse({
            'success': False,
            'message': '请提供评论信息'
        })
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '评论不存在'
        })
    if user.is_admin:
        comment.is_top = False
        comment.save()
        return JsonResponse({
            'success': True,
            'message': '取消置顶评论成功'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '无权限取消置顶评论'
        })
