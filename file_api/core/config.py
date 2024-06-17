import os
from logging import config as logging_config
from pydantic import BaseSettings, Field
from app.core.logger import LOGGING


class DataBaseSettings(BaseSettings):
    user: str = ...
    password: str = ...
    db: str = ...
    host: str = ...
    port: int = ...

    class Config:
        env_file = '.env'
        env_prefix = 'POSTGRES_'

    @property
    def url(self):
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


class Settings(BaseSettings):
    # App
    project_name: str = Field(default='File API', env='File API')
    uvicorn_host: str = Field(default='0.0.0.0', env='FILE_API_UVICORN_HOST')
    uvicorn_port: int = Field(default=8081, env='FILE_API_UVICORN_PORT')

    # Redis
    redis_host: str = Field(default='0.0.0.0', env='REDIS_HOST')
    redis_port: int = Field(default=6379, env='REDIS_PORT')

    # Elastic
    elastic_host: str = Field(default='0.0.0.0', env='ELASTIC_HOST')
    elastic_port: int = Field(default=9200, env='ELASTIC_PORT')

    # MinIO
    minio_host: str = Field(default='0.0.0.0', env='MINIO_HOST')
    minio_port: int = Field(default=9000, env='MINIO_PORT')
    minio_root_user: str = Field(default='practicum', env='MINIO_ROOT_USER')
    minio_root_password: str = Field(default='StrongPass', env='MINIO_ROOT_PASSWORD')
    backet_name: str = Field(default='movies', env='BACKET_NAME')

    # DB
    db: DataBaseSettings = DataBaseSettings()
    log_sql_queries: bool = False

    class Config:
        env_file = '.env'


# Создаем экземпляр класса Settings для хранения настроек
settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
