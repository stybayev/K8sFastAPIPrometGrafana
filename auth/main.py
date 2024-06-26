from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, JWTDecodeError
from redis.asyncio import Redis
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

from auth.api.v1 import users, roles
from auth.core.config import settings
from auth.core.jwt import JWTSettings
from auth.db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    AuthJWT.load_config(lambda: JWTSettings())
    redis.connection = Redis(host=settings.redis_host, port=settings.redis_port)

    # TODO: создание БД реализован через alembic, но строку оставлю пака на всякий пожарный
    # await create_database()

    yield

    await redis.connection.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/auth/openapi',
    openapi_url='/api/auth/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url='/api/v1/auth/users/login'
)


# Исключение при ошибке JWT
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "detail": exc.message
        }
    )


redis_client = Redis(host=settings.redis_host, port=settings.redis_port)


@app.middleware("http")
async def check_blacklist(request: Request, call_next):
    # Пока работает только с access_token (нужно определиться, как мы будем передавать рефреш)
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

        except JWTDecodeError as e:
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


app.include_router(users.router, prefix='/api/v1/auth/users', tags=['users'])
app.include_router(roles.router, prefix='/api/v1/auth/roles', tags=['roles'])
