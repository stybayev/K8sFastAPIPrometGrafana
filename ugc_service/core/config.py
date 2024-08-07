from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="UGC_")
    # App
    service_name: str
    service_uvicorn_host: str
    service_uvicorn_port: int


settings = Settings()
