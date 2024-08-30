FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app
RUN /usr/local/bin/python -m pip install --upgrade pip \
&& apt-get update -y \
&& apt-get install gcc -y \
&& pip install -r requirements.txt
COPY . /app

CMD uvicorn --reload --host=$UVICORN_HOST --port=$UVICORN_PORT app.main:app

