FROM python:3.10.4

WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python src/main.py runserver
