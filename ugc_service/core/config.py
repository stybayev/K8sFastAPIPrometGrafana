from flask import Flask
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="UGC_")
    # App
    service_name: str
    service_uvicorn_host: str
    service_uvicorn_port: int

    # JWT
    jwt_secret_key: str

    # Redis
    redis_host: str
    redis_port: int

    # Kafka
    bootstrap_servers: str


settings = Settings()


def init_config(app: Flask) -> None:
    app.config["SERVICE_NAME"] = settings.service_name
    app.config["SERVICE_UVICORN_HOST"] = settings.service_uvicorn_host
    app.config["SERVICE_UVICORN_PORT"] = settings.service_uvicorn_port
    app.config["JWT_SECRET_KEY"] = settings.jwt_secret_key
