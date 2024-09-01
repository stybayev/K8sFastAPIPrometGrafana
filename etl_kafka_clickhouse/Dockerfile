FROM python:3.10-slim

WORKDIR /etl_kafka_clickhouse

COPY . /etl_kafka_clickhouse

RUN apt-get update -y &&  \
    apt-get upgrade -y && \
    pip install -r requirements.txt


CMD ["python", "etl_processing.py"]
