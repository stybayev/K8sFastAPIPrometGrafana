FROM --platform=linux/amd64 python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /ugc_service
COPY requirements.txt /ugc_service
RUN /usr/local/bin/python -m pip install --upgrade pip \
&& apt-get update -y \
&& apt-get install gcc -y \
&& pip install -r requirements.txt \
&& pip install --upgrade 'sentry-sdk[flask]'
COPY . /ugc_service

CMD ["sh", "-c", "echo 'Starting Gevent WSGI Server...' && python ugc_service/pywsgi.py"]
