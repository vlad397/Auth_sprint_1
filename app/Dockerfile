FROM python:3.9.12-slim-buster

WORKDIR /app/

RUN apt update &&\
    apt install -y curl

ADD requirements.txt /app
RUN pip3 install -r requirements.txt

ADD /app /app

EXPOSE 8000/tcp

ENTRYPOINT\
        python3 manage.py migrate &&\
        python3 manage.py createsuperuser --noinput --username admin --email admin@localhost &&\
        cd /app &&\
        gunicorn config.wsgi\
                --bind 0.0.0.0:8000 \
                --workers 4 \
                --chdir /app/ \
                --log-file -
