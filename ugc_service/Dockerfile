FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /ugc
COPY requirements.txt /ugc
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update -y
RUN apt-get install gcc -y
RUN pip install -r requirements.txt
COPY . /ugc

# Добавляем entrypoint.sh
COPY entrypoint.sh /ugc/entrypoint.sh

RUN chmod +x /ugc/entrypoint.sh

ENTRYPOINT ["/ugc/entrypoint.sh"]
