FROM python:3.10.4

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .