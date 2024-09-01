from pydantic import BaseSettings

from rating_review_service.core.config import settings


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_algorithm: str = settings.ALGORITHM
    authjwt_access_token_expires: int = settings.ACCESS_TOKEN_EXPIRES
    authjwt_refresh_token_expires: int = settings.REFRESH_TOKEN_EXPIRES
    authjwt_user_claims: bool = True
