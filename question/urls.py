from django.urls import path
from .views import *

urlpatterns = [
    path('question/list', get_questions_view),
    path('question/upload', upload_image_view),
    path('question', QuestionView.as_view()),
    path('answer', AnswerView.as_view()),
]
