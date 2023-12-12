from django.db import models

from enum import Enum

from user.models import User


# Create your models here.

class Author(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    profile = models.TextField(null=True)
    avatar = models.CharField(max_length=100, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    reason = models.TextField(null=True)
    phone_number = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ApplicationStatus(Enum):
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
