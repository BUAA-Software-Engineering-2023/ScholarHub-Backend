from django.db import models

from user.models import User


# Create your models here.

class Message(models.Model):
    is_read = models.BooleanField(default=False)
    content = models.TextField()
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
