# import os
#
# from pydantic_settings import BaseSettings
#
#
# class Settings(BaseSettings):
#     # clickhouse
#     clickhouse_port: int = int(os.getenv('CLICKHOUSE_PORT'))
#     clickhouse_poll_records: int = int(os.getenv('CLICKHOUSE_POLL_RECORDS'))
#
#     # kafka
#     kafka_bootstrap_servers: list[str] = os.getenv('KAFKA_BOOTSTRAP_SERVERS').split(',')
#     kafka_topics: list[str] = os.getenv('KAFKA_TOPICS').split(',')
#     kafka_consumer_group_id: str = os.getenv('CONSUMER_GROUP_ID')
#
#
# settings = Settings()
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):

    kafka_topics: str
    kafka_bootstrap_servers: str
    kafka_consumer_group_id: str

    clickhouse_host: str
    clickhouse_port: int
    clickhouse_poll_records: int

    class Config:
        env_file = ".env"


try:
    settings = Settings()
except ValidationError as e:
    print(f"Error in settings: {e}")
    raise
