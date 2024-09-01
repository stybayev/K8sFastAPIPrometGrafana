from functools import wraps

from fastapi import HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException


def access_token_required(func):
    @wraps(func)
    async def wrapper(self, authorize: AuthJWT, *args, **kwargs):
        try:
            authorize.jwt_required()
        except AuthJWTException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid access token'
            )
        return await func(self, authorize, *args, **kwargs)
    return wrapper
