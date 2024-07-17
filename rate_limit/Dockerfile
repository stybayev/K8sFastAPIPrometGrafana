FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /rate_limit
COPY requirements.txt /rate_limit
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update -y
RUN apt-get install gcc -y
RUN pip install -r requirements.txt
COPY . /rate_limit

CMD uvicorn --reload --host=$RATE_LIMIT_HOST --port=$RATE_LIMIT_PORT rate_limit.main:app