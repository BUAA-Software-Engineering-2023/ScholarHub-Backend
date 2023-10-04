from django.db import models


class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
