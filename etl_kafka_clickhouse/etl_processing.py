import asyncio
import json
import logging
from typing import List, Optional

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError, ServerException

from settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

topics = settings.kafka_topics.split(',')
bootstrap_servers = settings.kafka_bootstrap_servers.split(',')
group_id = settings.kafka_consumer_group_id
poll_records = settings.clickhouse_poll_records
clickhouse_host = settings.clickhouse_host
clickhouse_port = settings.clickhouse_port

async def consume() -> None:
    """
    Асинхронная функция, которая создает Kafka-консюмер, читает сообщения из Kafka и передает их в ClickHouse.

    Функция создает Kafka-консюмер, который подключается к нескольким топикам и считывает сообщения пакетами
    по 10 штук. После того, как пакет собран, сообщения отправляются на запись в ClickHouse. В случае успеха
    смещения подтверждаются и консюмер продолжает обработку следующих сообщений.
    """
    consumer: Optional[AIOKafkaConsumer] = None
    try:
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id='movies',
            enable_auto_commit=False,  # Отключаем авто-подтверждение смещений
            auto_offset_reset='earliest',
            max_poll_records=poll_records
        )
        logger.info("KafkaConsumer instance created")

        await consumer.start()
        logger.info("Kafka consumer started")
        while True:
            messages: List[ConsumerRecord] = []
            async for message in consumer:
                messages.append(message)
                logger.info(f"Count messages: {len(messages)}")
                if len(messages) >= poll_records:  # Как только накопилось {poll_records} сообщений, сохраняем их в ClickHouse
                    success: bool = await save_to_clickhouse(messages)
                    if success:
                        await consumer.commit()  # Подтверждаем смещения после успешной записи
                        messages.clear()

    except Exception as e:
        logger.error(f"Error while consuming messages: {e}")

    finally:
        if consumer:
            await consumer.stop()
            logger.info("Kafka consumer stopped")


async def save_to_clickhouse(messages: List[ConsumerRecord]) -> bool:
    """
    Асинхронная функция, которая записывает сообщения из Kafka в ClickHouse.

    :param messages: Список сообщений Kafka для записи.
    :return: Булево значение, указывающее на успешность операции.

    Функция принимает список сообщений, подготовленных из Kafka, и записывает их в таблицу `events`
    базы данных ClickHouse. В случае возникновения ошибки при подключении или записи в ClickHouse,
    функция возвращает False, иначе True.
    """
    try:
        client: Client = Client(host=clickhouse_host)

        data_to_insert: List[tuple] = []
        for message in messages:
            msg: dict = json.loads(message.value.decode('utf-8'))
            data_to_insert.append((
                msg.get('event_type'),
                msg.get('source'),
                msg.get('timestamp'),
                json.dumps(msg.get('data', {}))
            ))

        query: str = """
        INSERT INTO movies.events (event_type, source, timestamp, data) VALUES
        """
        client.execute(query, data_to_insert)

        logger.info("Data successfully inserted into ClickHouse")
        return True
    except (NetworkError, ServerException) as e:
        logger.error(f"Failed to connect to ClickHouse: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to insert messages into ClickHouse: {e}")
        return False


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        logger.info("Starting ETL process")
        loop.run_until_complete(consume())
    finally:
        loop.close()
        logger.info("ETL process finished")
