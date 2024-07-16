import os
from logging import config as logging_config

from app.core.logger import LOGGING
from pydantic import BaseSettings, Field


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
    project_name: str = Field(default='Auth API', env='File API')
    uvicorn_host: str = Field(default='0.0.0.0', env='AUTH_API_UVICORN_HOST')
    uvicorn_port: int = Field(default=8082, env='AUTH_API_UVICORN_PORT')

    # Redis
    redis_host: str = Field(default='0.0.0.0', env='REDIS_HOST')
    redis_port: int = Field(default=6379, env='REDIS_PORT')

    # Postgres
    db: DataBaseSettings = DataBaseSettings()
    log_sql_queries: bool = False

    # JWT
    SECRET_KEY: str = Field(default='secret_key', env='JWT_SECRET_KEY')
    ALGORITHM: str = Field(default='HS256', env='ALGORITHM')
    ACCESS_TOKEN_EXPIRES: int = Field(default=30, env='ACCESS_TOKEN_EXPIRES')
    REFRESH_TOKEN_EXPIRES: int = Field(default=1440, env='REFRESH_TOKEN_EXPIRES')

    # OAuth2
    YANDEX_CLIENT_ID: str = Field(default='client_id', env='YANDEX_CLIENT_ID')
    YANDEX_CLIENT_SECRET: str = Field(default='client_secret', env='YANDEX_CLIENT_SECRET')
    YANDEX_REDIRECT_URI: str = Field(default='http://0.0.0.0:8082/api/v1/auth/yandex/callback',
                                     env='YANDEX_REDIRECT_URI')

    class Config:
        env_file = '.env'


# Создаем экземпляр класса Settings для хранения настроек
settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
