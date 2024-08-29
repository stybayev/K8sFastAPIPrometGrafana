import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from app.core.logger import LOGGING

class DataBaseSettings(BaseSettings):
    initdb_root_username: str = ...
    initdb_root_password: str = ...
    default_database: str = ...
    host: str = ...
    port: int = ...

    class Config:
        env_file = ".env"
        env_prefix = "MONGO_"

    @property
    def url(self):
        return f"mongodb://{self.initdb_root_username}:{self.initdb_root_password}@{self.host}:{self.port}"


class Settings(BaseSettings):
    project_name: str = ...

    # MongoDB
    db: DataBaseSettings = DataBaseSettings()

    class Config:
        env_file = ".env"
        env_prefix = "RATING_REVIEW_SERVICE_"


settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
