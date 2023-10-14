import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from question.task import *
from utils.cache import get_question_cache, set_question_cache, clear_question_cache, get_answer_cache, \
    set_answer_cache, clear_answer_cache
from utils.decorator import request_methods
from utils.token import auth_check
from utils.upload import upload_file


# Create your views here.


class QuestionView(View):
    def get(self, request):
        questions = get_question_cache()
        if not questions:
            questions = Question.objects.all()
            questions = [{
                'question_id': question.id,
                'title': question.title,
                'asker_id': question.asker.id,
                'asker_nickname': question.asker.nickname,
                'content': question.content,
                'created_at': question.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': question.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            } for question in questions]
            set_question_cache(questions)
        return JsonResponse({
            'success': True,
            'data': questions,
        })

    @method_decorator(auth_check)
    def post(self, request):
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        asker = request.user
        if not title or not content:
            return JsonResponse({
                'success': False,
                'message': '标题和内容不能为空',
            })
        celery_create_question.delay(title, content, asker.id)
        clear_question_cache()
        return JsonResponse({
            'success': True,
            'message': '问题已发表',
        })

    @method_decorator(auth_check)
    def put(self, request):
        data = json.loads(request.body)
        question_id = data.get('question_id')
        if not question_id:
            return JsonResponse({
                'success': False,
                'message': '问题id不能为空',
            })
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '问题不存在',
            })
        if question.asker != request.user:
            return JsonResponse({
                'success': False,
                'message': '只能修改自己的问题',
            })
        title = data.get('title', question.title)
        content = data.get('content', question.content)
        question.title = title
        question.content = content
        question.save()
        clear_question_cache()
        return JsonResponse({
            'success': True,
            'data': {
                'question_id': question.id,
                'title': question.title,
                'content': question.content,
                'asker_id': question.asker.id,
                'asker_nickname': question.asker.nickname,
                'created_at': question.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': question.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })

    @method_decorator(auth_check)
    def delete(self, request):
        data = json.loads(request.body)
        question_id = data.get('question_id')
        if not question_id:
            return JsonResponse({
                'success': False,
                'message': '问题id不能为空',
            })
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '问题不存在',
            })
        if (not request.user.is_admin) and question.asker != request.user:
            return JsonResponse({
                'success': False,
                'message': '只能删除自己的问题',
            })
        question.delete()
        clear_question_cache()
        return JsonResponse({
            'success': True,
            'message': '删除成功',
        })


class AnswerView(View):
    def get(self, request):
        question_id = request.GET.get('question_id')
        if not question_id:
            return JsonResponse({
                'success': False,
                'message': '问题id不能为空',
            })
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '问题不存在',
            })
        answers = get_answer_cache(question_id)
        if not answers:
            answers = question.answer_set.all()
            answers = [{
                'answer_id': answer.id,
                'content': answer.content,
                'answerer_id': answer.answerer.id,
                'answerer_nickname': answer.answerer.nickname,
                'created_at': answer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': answer.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            } for answer in answers]
            set_answer_cache(question_id, answers)
        return JsonResponse({
            'success': True,
            'data': answers,
        })

    @method_decorator(auth_check)
    def post(self, request):
        data = json.loads(request.body)
        question_id = data.get('question_id')
        content = data.get('content')
        answerer = request.user
        if not (question_id and content):
            return JsonResponse({
                'success': False,
                'message': '问题id和内容不能为空',
            })
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '问题不存在',
            })
        celery_create_answer.delay(question_id, content, answerer.id)
        clear_answer_cache(question_id)
        celery_create_message.delay(question.asker.id,
                                    '{}回答了你的问题：{}'.format(answerer.nickname, question.title))
        return JsonResponse({
            'success': True,
            'message': '回答已发表',
        })

    @method_decorator(auth_check)
    def put(self, request):
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        if not answer_id:
            return JsonResponse({
                'success': False,
                'message': '回答id不能为空',
            })
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '回答不存在',
            })
        if answer.answerer != request.user:
            return JsonResponse({
                'success': False,
                'message': '只能修改自己的回答',
            })
        content = data.get('content', answer.content)
        answer.content = content
        answer.save()
        clear_answer_cache(answer.question.id)
        return JsonResponse({
            'success': True,
            'data': {
                'answer_id': answer.id,
                'content': answer.content,
                'answerer_id': answer.answerer.id,
                'answerer_nickname': answer.answerer.nickname,
                'created_at': answer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': answer.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })

    @method_decorator(auth_check)
    def delete(self, request):
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        if not answer_id:
            return JsonResponse({
                'success': False,
                'message': '回答id不能为空',
            })
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '回答不存在',
            })
        if (not request.user.is_admin) and answer.answerer != request.user:
            return JsonResponse({
                'success': False,
                'message': '只能删除自己的回答',
            })
        answer.delete()
        clear_answer_cache(answer.question.id)
        return JsonResponse({
            'success': True,
            'message': '删除成功',
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
