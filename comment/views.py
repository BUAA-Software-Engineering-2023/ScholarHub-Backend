import json

from django.http import JsonResponse

from comment.models import Comment
from message.models import Message
from utils.cache import get_comment_cache, set_comment_cache, clear_comment_cache
from utils.decorator import request_methods
from utils.openalex import get_single_entity
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
    comments = get_comment_cache(work_id)
    if not comments:
        if reverse or reverse is None:
            comments = Comment.objects.filter(work=work_id).order_by('-created_at')
        else:
            comments = Comment.objects.filter(work=work_id).order_by('created_at')
        temp = {}
        for comment in comments:
            if not comment.reply:
                continue
            if comment.reply.id not in temp:
                temp[comment.reply.id] = []
            temp[comment.reply.id].append(comment)

        def build_comment_tree(comment):
            return {
                'comment_id': comment.id,
                'work_id': comment.work,
                'sender_id': comment.sender.id,
                'sender_username': comment.sender.username,
                'content': comment.content,
                'replies': [build_comment_tree(reply) for reply in temp.get(comment.id, [])],
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }

        temp2 = []
        for comment in comments:
            if not comment.reply:
                temp2.append(build_comment_tree(comment))
        comments = temp2
        set_comment_cache(work_id, comments)
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
        comment = Comment(work=work_id, sender=request.user, content=content, reply=reply)
        comment.save()
        clear_comment_cache(comment.work)
        message = Message(receiver=reply.sender, content=f'您的评论有了来自{request.user.username}的新回复')
        message.save()
        return JsonResponse({
            'success': True,
            'message': '回复评论成功',
            'data': {
                'comment_id': comment.id,
                'work_id': comment.work,
                'sender_id': comment.sender.id,
                'sender_username': comment.sender.username,
                'content': comment.content,
                'reply_id': comment.reply.id,
                'reply_username': comment.reply.sender.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })
    else:
        comment = Comment(work=work_id, sender=request.user, content=content)
        comment.save()
        clear_comment_cache(comment.work)
        return JsonResponse({
            'success': True,
            'message': '评论成功',
            'data': {
                'comment_id': comment.id,
                'work_id': comment.work,
                'sender_id': comment.sender.id,
                'sender_username': comment.sender.username,
                'content': comment.content,
                'reply_id': None,
                'reply_username': None,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
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
    if user.is_admin:
        comment.delete()
        clear_comment_cache(comment.work)
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
        clear_comment_cache(comment.work)
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
    clear_comment_cache(comment.work)
    return JsonResponse({
        'success': True,
        'message': '修改评论成功',
        'data': {
            'comment_id': comment.id,
            'work_id': comment.work,
            'sender_id': comment.sender.id,
            'sender_username': comment.sender.username,
            'content': comment.content,
            'reply_id': comment.reply.id if comment.reply else None,
            'reply_username': comment.reply.sender.username if comment.reply else None,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
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
