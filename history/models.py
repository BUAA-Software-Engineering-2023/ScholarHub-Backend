from django.db import models

from user.models import User


# Create your models here.

class History(models.Model):
    title = models.CharField(max_length=100)
    work = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
