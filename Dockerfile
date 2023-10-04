FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /django/ScholarHub

# 设置容器内工作目录
WORKDIR /django/ScholarHub

# 将当前目录文件拷贝一份到工作目录中
ADD . /django/ScholarHub

# 利用 pip 安装依赖
RUN pip install -r requirements.txt

RUN chmod 777 /django/ScholarHub/media

EXPOSE 8000

CMD python manage.py makemigrations && python manage.py migrate && uwsgi --ini /django/ScholarHub/uwsgi.ini
