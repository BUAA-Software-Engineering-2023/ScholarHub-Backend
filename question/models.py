from django.db import models

from user.models import User


# Create your models here.

class Question(models.Model):
    work = models.CharField(max_length=100)
    title = models.TextField()
    asker = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answerer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def info(self):
        return {
            'id': self.id,
            'content': self.content,
            'answerer_id': self.answerer.id,
            'answerer_nickname': self.answerer.nickname,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
