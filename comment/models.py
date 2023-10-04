from django.db import models

from user.models import User


# Create your models here.

class Comment(models.Model):
    work = models.CharField(max_length=100)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
