FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt  \
     && pip install --upgrade sentry-sdk

COPY . .

CMD python -m load_data
