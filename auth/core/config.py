from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DataBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='POSTGRES_')
    user: str = ...
    password: str = ...
    db: str = ...
    host: str = ...
    port: int = ...

    @property
    def url(self):
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='allow')
    # App
    project_name: str = 'Auth API'
    auth_api_uvicorn_host: str = '0.0.0.0'
    auth_api_uvicorn_port: int = 8082

    # Redis
    redis_host: str = '0.0.0.0'
    redis_port: int = 6379

    # Postgres
    db: DataBaseSettings = DataBaseSettings()
    log_sql_queries: bool = False

    # JWT
    secret_key: str = 'practicum'
    algorithm: str = 'HS256'
    access_token_expires: int = 30
    refresh_token_expires: int = 1410

settings = Settings()

# Применяем настройки логирования
from logging import config as logging_config
from app.core.logger import LOGGING
logging_config.dictConfig(LOGGING)

# Корень проекта
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
