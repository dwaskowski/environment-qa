FROM php:5.6-cli
RUN apt-get update \
    && docker-php-ext-install mysql
ADD . /web
