FROM python:3.11-alpine
MAINTAINER "Jari Van Melckebeke <jarivanmelckebeke@gmail.com>"
LABEL version="1.0"
LABEL description="small script that checks traefik servers and updates adguard rewrites, wrapped in a cronjob"

WORKDIR /app

ADD requirements.txt .

RUN pip install --no-cache -r requirements.txt

ADD ./app /app

ADD crontab /etc/crontabs/root

RUN chmod 600 /etc/crontabs/root

ENTRYPOINT ["crond", "-f"]