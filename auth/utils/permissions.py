from functools import wraps

from fastapi import HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException


def admin_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        Authorize = kwargs.get('Authorize') or args[0]
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")
        return await func(self, *args, **kwargs)

    return wrapper


def refresh_token_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        authorize = kwargs.get('authorize') or args[0]
        if not isinstance(authorize, AuthJWT):
            raise ValueError(
                "Authorize object must be passed as a keyword argument 'authorize' or as the first positional argument")

        try:
            authorize.jwt_refresh_token_required()
        except AuthJWTException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid refresh token'
            )

        return await func(self, *args, **kwargs)

    return wrapper


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
