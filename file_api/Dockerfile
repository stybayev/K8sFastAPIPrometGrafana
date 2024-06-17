FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /file_api
COPY requirements.txt /file_api
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update -y
RUN apt-get install gcc -y
RUN pip install -r requirements.txt
COPY . /file_api

CMD uvicorn --reload --host=$FILE_API_UVICORN_HOST --port=$FILE_API_UVICORN_PORT file_api.main:app
