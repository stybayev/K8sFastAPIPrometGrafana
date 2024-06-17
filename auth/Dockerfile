FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /auth
COPY requirements.txt /auth
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update -y
RUN apt-get install gcc -y
RUN pip install -r requirements.txt
COPY . /auth

CMD uvicorn --reload --host=$AUTH_API_UVICORN_HOST --port=$AUTH_API_UVICORN_PORT auth.main:app
