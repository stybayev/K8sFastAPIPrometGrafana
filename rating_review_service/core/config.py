import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from app.core.logger import LOGGING


class Settings(BaseSettings):
    project_name: str = ...

    class Config:
        env_file = ".env"
        env_prefix = "RATING_REVIEW_SERVICE_"


settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
