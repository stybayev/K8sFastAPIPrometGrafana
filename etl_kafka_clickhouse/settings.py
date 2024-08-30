from pydantic import ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    kafka_topics: str
    kafka_bootstrap_servers: str
    kafka_consumer_group_id: str

    clickhouse_host: str
    clickhouse_port: int
    clickhouse_poll_records: int

    jwt_secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"


try:
    settings = Settings()
except ValidationError as e:
    print(f"Error in settings: {e}")
    raise
