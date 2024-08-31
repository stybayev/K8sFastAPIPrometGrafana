import os
from logging import config as logging_config
from pydantic import BaseSettings, Field
from app.core.logger import LOGGING


class Settings(BaseSettings):
    project_name: str = Field(default="movies", env="movies")
    uvicorn_host: str = Field(default="0.0.0.0", env="UVICORN_HOST")
    uvicorn_port: int = Field(default=8000, env="UVICORN_PORT")
    redis_host: str = Field(default="0.0.0.0", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    elastic_host: str = Field(default="0.0.0.0", env="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, env="ELASTIC_PORT")
    secret_key: str = Field(default='practicum', env="JWT_SECRET_KEY")
    algorithm: str = Field(default='HS256', env="HS256")

    class Config:
        env_file = ".env"


# Создаем экземпляр класса Settings для хранения настроек
settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
