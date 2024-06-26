# middleware.py
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, JWTDecodeError
from redis.asyncio import Redis
from auth.core.config import settings

redis_client = Redis(host=settings.redis_host, port=settings.redis_port)


async def check_blacklist(request: Request, call_next):
    token = request.headers.get("Authorization")
    if token:
        try:
            # По умолчанию fastapi-jwt-auth в заготовок к токену добавляет Bearer
            access_token = token[len("Bearer "):]  # Удаление префикса 'Bearer '
            Authorize = AuthJWT()
            raw_jwt = Authorize.get_raw_jwt(encoded_token=access_token)
            jti = raw_jwt.get('jti')

            if await redis_client.get(jti) == "blacklisted":
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

    response = await call_next(request)
    return response
