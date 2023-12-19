import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from message.models import Message
from utils.decorator import request_methods
from utils.token import auth_check


# Create your views here.

class MessageView(View):
    @method_decorator(auth_check)
    def get(self, request):
        user = request.user
        messages = Message.objects.filter(receiver=user)
        messages = [{
            'message_id': message.id,
            'receiver': message.receiver.id,
            'receiver_username': message.receiver.username,
            'content': message.content,
            'is_read': message.is_read,
            'created_at': message.created_at.strftime('%Y-%m-%d'),
        } for message in messages]
        return JsonResponse({
            'success': True,
            'data': messages
        })

    @method_decorator(auth_check)
    def delete(self, request):
        data = json.loads(request.body)
        user = request.user
        message_id = data.get('message_id')
        if not message_id:
            return JsonResponse({
                'success': False,
                'message': '请提供消息信息'
            })
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '消息不存在'
            })
        if message.receiver != user:
            return JsonResponse({
                'success': False,
                'message': '消息显示异常'
            })
        message.delete()
        return JsonResponse({
            'success': True,
            'message': '删除成功'
        })

    @method_decorator(auth_check)
    def put(self, request):
        messages = Message.objects.filter(receiver=request.user, is_read=False)
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse({
            'success': True,
            'message': '消息全部已读'
        })


@request_methods('PUT')
@auth_check
def read_message_view(request):
    data = json.loads(request.body)
    message_id = data.get('message_id')
    if not message_id:
        return JsonResponse({
            'success': False,
            'message': '请提供消息信息'
        })
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '消息不存在'
        })
    if message.receiver != request.user:
        return JsonResponse({
            'success': False,
            'message': '消息显示异常'
        })
    message.is_read = True
    message.save()
    return JsonResponse({
        'success': True,
        'message': '消息已读'
    })
