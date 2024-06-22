from pydantic import BaseSettings


class TestSettings(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379

    class Config:
        env_file = '.env.test'
        env_prefix = 'TEST_'


test_settings = TestSettings()
