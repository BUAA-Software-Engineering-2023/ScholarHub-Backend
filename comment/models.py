from django.db import models

from user.models import User


# Create your models here.

class Comment(models.Model):
    work = models.CharField(max_length=100)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_top = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def info(self):
        return {
            'comment_id': self.id,
            'work_id': self.work,
            'sender_id': self.sender.id,
            'sender_nickname': self.sender.nickname,
            'sender_avatar': self.sender.avatar if self.sender.avatar else "https://img.zcool.cn/community/0177b355ed01bc6ac7251df8f6be5a.png",
            'content': self.content,
            'reply_id': self.reply.id if self.reply else None,
            'comments': [comment.info() for comment in self.comment_set.all()],
            'is_top': self.is_top,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
