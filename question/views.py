import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from question.task import *
from utils.cache import *
from utils.decorator import request_methods
from utils.token import auth_check
from utils.upload import upload_file


# Create your views here.


class QuestionView(View):
    def get(self, request):
        question_id = request.GET.get('question_id')
        if question_id:
            question = get_question_cache(question_id)
            if not question:
                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': '问题不存在',
                    })
                question = {
                    'question_id': question.id,
                    'title': question.title,
                    'asker_id': question.asker.id,
                    'asker_nickname': question.asker.nickname,
                    'content': question.content,
                    'created_at': question.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': question.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'answers': [answer.info() for answer in question.answer_set.all().order_by('-created_at')]
                }
                set_question_cache(question, question_id)
            return JsonResponse({
                'success': True,
                'data': question,
            })
        else:
            questions = get_questions_cache()
            if not questions:
                questions = Question.objects.all().order_by('-created_at')
                questions = [{
                    'question_id': question.id,
                    'title': question.title,
                    'asker_id': question.asker.id,
                    'asker_nickname': question.asker.nickname,
                    'content': question.content,
                    'created_at': question.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': question.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'answers': [answer.info() for answer in question.answer_set.all().order_by('-created_at')]
                } for question in questions]
                set_questions_cache(questions)
            return JsonResponse({
                'success': True,
                'data': questions,
            })

    @method_decorator(auth_check)
    def post(self, request):
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        work_id = data.get('work_id')
        asker = request.user
        if not title or not content:
            return JsonResponse({
                'success': False,
                'message': '标题、内容及论文id不能为空',
            })
        celery_create_question.delay(work_id, title, content, asker.id)
        clear_questions_cache()
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
        clear_questions_cache()
        clear_question_cache(question_id)
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
        clear_questions_cache()
        clear_question_cache(question_id)
        return JsonResponse({
            'success': True,
            'message': '删除成功',
        })


class AnswerView(View):
    def get(self, request):
        answer_id = request.GET.get('answer_id')
        if not answer_id:
            return JsonResponse({
                'success': False,
                'message': '回答id不能为空',
            })
        answer = get_answer_cache(answer_id)
        if not answer:
            try:
                answer = Answer.objects.get(id=answer_id)
            except Answer.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '问题不存在',
                })
            answer = {
                'answer_id': answer.id,
                'content': answer.content,
                'answerer_id': answer.answerer.id,
                'answerer_nickname': answer.answerer.nickname,
                'created_at': answer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': answer.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            set_answer_cache(answer_id, answer)
        return JsonResponse({
            'success': True,
            'data': answer,
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
        clear_questions_cache()
        clear_question_cache(question_id)
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
        clear_answer_cache(answer_id)
        clear_questions_cache()
        clear_question_cache(answer.question.id)
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
        clear_answer_cache(answer_id)
        clear_questions_cache()
        clear_question_cache(answer.question.id)
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
