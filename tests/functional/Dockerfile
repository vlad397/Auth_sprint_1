FROM python:3.9.12-slim-buster

WORKDIR /

ADD tests/functional/requirements.txt /

RUN pip3 install -r requirements.txt

ADD / /

ENTRYPOINT\
        cd /tests/functional && pytest -vv

