import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    project_name: str = Field(default="UGC Service", env="UGC_SERVICE_NAME")
    uvicorn_host: str = Field(default="0.0.0.0", env="UGC_SERVICE_UVICORN_HOST")
    uvicorn_port: int = Field(default=8084, env="UGC_SERVICE_UVICORN_PORT")

    class Config:
        env_file = ".env"


settings = Settings()
