FROM nginx

RUN rm /etc/nginx/conf.d/*
RUN mkdir -p /usr/django/media
RUN chown -R www-data:www-data /usr/django/media
RUN chmod -R 777 /usr/django/media

ADD nginx.conf /etc/nginx/conf.d/

CMD ["nginx", "-g", "daemon off;"]