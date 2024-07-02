from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, JWTDecodeError
from redis.asyncio import Redis

from auth.core.config import settings

redis_client = Redis(host=settings.redis_host, port=settings.redis_port)


async def check_blacklist(request: Request, call_next):
    Authorize = AuthJWT()
    token = request.headers.get("Authorization")
    refresh_token = request.headers.get("X-Refresh-Token")
    if token:
        try:
            access_token = token[len("Bearer "):]  # Удаление префикса 'Bearer '
            raw_jwt = Authorize.get_raw_jwt(encoded_token=access_token)
            jti = raw_jwt.get('jti')

            if await redis_client.get(f"invalid_token:{jti}"):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token is blacklisted"}
                )

        except JWTDecodeError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"}
            )
        except AuthJWTException as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )

    if refresh_token:
        try:
            raw_jwt = Authorize.get_raw_jwt(encoded_token=refresh_token)
            jti = raw_jwt.get('jti')

            if await redis_client.get(f"invalid_token:{jti}"):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Refresh token is blacklisted"}
                )

        except JWTDecodeError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid refresh token"}
            )
        except AuthJWTException as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )

    response = await call_next(request)
    return response
