from pydantic import BaseSettings


class TestSettings(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379

    class Config:
        env_file = '.env.test'
        env_prefix = 'TEST_'

class TestJWTSettings(BaseSettings):
    authjwt_secret_key: str = 'practicum'
    authjwt_algorithm: str = 'HS256'
    authjwt_access_token_expires: int = 30
    authjwt_refresh_token_expires: int = 1410
    authjwt_user_claims: bool = True


test_settings = TestSettings()
