import logging.config

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBParams(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", env_file="../.env")

    host: str
    port: str
    db: str
    user: str
    password: str

    def url(self):
        return f"{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class ElasticParams(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELASTIC_", env_file="../.env")

    host: str
    port: str
    index_name: str = "movies"

    def url(self):
        return f"{self.host}:{self.port}"


class RedisParams(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file="../.env")

    host: str
    port: str

    def url(self):
        return f"{self.host}:{self.port}"


with open("log_config.yaml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    logging.basicConfig(level=logging.INFO)
