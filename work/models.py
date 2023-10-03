from enum import Enum

from django.db import models

from author.models import Author


# Create your models here.

class Work(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WorkStatus(Enum):
    PENDING = '1'
    ACCEPTED = '2'
    REJECTED = '3'

    def info(self):
        if self.value == '1':
            return '待审核'
        elif self.value == '2':
            return '已通过'
        elif self.value == '3':
            return '已拒绝'
