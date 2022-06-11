FROM python:3.9.12-slim-buster

WORKDIR /api/

RUN apt update &&\
    apt install -y curl gcc cmake

ADD requirements.txt /api
RUN pip3 install -r requirements.txt

RUN python --version

ADD / /api

EXPOSE 8000/tcp

ENTRYPOINT\
        cd /api &&\
        gunicorn main:app\
                --bind 0.0.0.0:8000 \
                -k uvicorn.workers.UvicornWorker\
                --workers 4 \
                --chdir /api/ \
                --log-file -
