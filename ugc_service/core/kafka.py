import json
from contextlib import contextmanager

from kafka import KafkaProducer
from typing import Generator

from core.config import settings


@contextmanager
def get_kafka_producer() -> Generator[KafkaProducer, None, None]:
    """
    Создание генератора для управления жизненным циклом KafkaProducer
    """
    producer = KafkaProducer(bootstrap_servers=[settings.bootstrap_servers])
    try:
        yield producer
    finally:
        producer.close()


def send_to_kafka(producer: KafkaProducer, topic: str, key: str, value: dict):
    """
    Функция для отправки события в соответствующий топик Kafka
    """
    producer.send(
        topic=topic,
        key=key.encode('utf-8'),
        value=json.dumps(value).encode('utf-8')
    )
