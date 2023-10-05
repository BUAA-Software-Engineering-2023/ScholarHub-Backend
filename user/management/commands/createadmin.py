from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from user.models import User

class Command(BaseCommand):
    help = '创建一个管理员，账号为：admin，密码为：buaa，需指定邮箱'

    def add_arguments(self, parser):
        parser.add_argument('email')

    def handle(self, *args, **options):
        email = options['email']
        try:
            validate_email(email)
        except ValidationError:
            self.stdout.write(self.style.ERROR('邮箱格式错误'))
            return
        user = User.objects.filter(username='admin').first()
        if not user:
            pssword = make_password('buaa')
            User.objects.create(username='admin', nickname='admin',
                                email=email, password=pssword, is_admin=True)
            self.stdout.write(self.style.SUCCESS('成功创建管理员，账号为：admin，密码为：buaa'))
        else:
            self.stdout.write(self.style.SUCCESS('已存在管理员'))