FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /auth
COPY requirements.txt /auth
RUN /usr/local/bin/python -m pip install --upgrade pip \
&& apt-get update -y \
&& apt-get install gcc -y \
&& pip install -r requirements.txt \
&& pip install --upgrade 'sentry-sdk[fastapi]'
COPY . /auth

CMD uvicorn --reload --host=$AUTH_API_UVICORN_HOST --port=$AUTH_API_UVICORN_PORT auth.main:app
