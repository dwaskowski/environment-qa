FROM nginx
MAINTAINER Dmitrij Waskowski <dymitr@gmail.com>

RUN rm /etc/nginx/conf.d/default.conf
ADD main/ /etc/nginx/conf.d
ADD local/ /etc/nginx/conf.d
