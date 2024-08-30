FROM python:3.10-slim

WORKDIR /etl_kafka_clickhouse

COPY . /etl_kafka_clickhouse

RUN apt-get update &&  \
    apt-get upgrade && \
    pip install -r requirements.txt && \
    && pip install --upgrade sentry-sdk


CMD ["python", "etl_processing.py"]
