from pydantic import BaseSettings

from auth.core.config import settings
from jose import jwt
import time
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import HTTPException, Request
import http


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_algorithm: str = settings.ALGORITHM
    authjwt_access_token_expires: int = settings.ACCESS_TOKEN_EXPIRES
    authjwt_refresh_token_expires: int = settings.REFRESH_TOKEN_EXPIRES
    authjwt_user_claims: bool = True


def decode_token(token: str) -> dict | None:
    """
    Функция декодирования токена
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    """
    Класс JWTBearer реализует метод __call__, который достает Bearer-токен из заголовка запроса.
    Если Bearer-токен отсутствует, то метод вернет ошибку.
    """
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail='Only Bearer token might be accepted')
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid or expired token.')
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt = JWTBearer()
