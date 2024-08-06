FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /ugc_service
COPY requirements.txt /ugc_service
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update -y
RUN apt-get install gcc -y
RUN pip install -r requirements.txt
COPY . /ugc_service

# Добавляем entrypoint.sh
COPY entrypoint.sh /ugc_service/entrypoint.sh

# Копируем .env файл
COPY .env /ugc_service/.env

RUN chmod +x /ugc_service/entrypoint.sh

ENV PYTHONPATH=/ugc_service

ENTRYPOINT ["/ugc_service/entrypoint.sh"]
