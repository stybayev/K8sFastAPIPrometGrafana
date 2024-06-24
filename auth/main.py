from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from redis.asyncio import Redis
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


# Middleware для проверки черного списка токенов
@app.middleware("http")
async def check_blacklist(request: Request, call_next):
    token = request.cookies.get("access_token")
    print('token=', token)
    if token:
        try:
            decoded_token = AuthJWT().decode_token(token)
            jti = decoded_token['jti']
            if redis_client.get(jti) == "blacklisted":
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token is blacklisted"},
                    media_type="application/json"
                )
        except AuthJWTException as e:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
                media_type="application/json"
            )

    response = await call_next(request)
    return response


app.include_router(users.router, prefix='/api/v1/auth/users', tags=['users'])
app.include_router(roles.router, prefix='/api/v1/auth/roles', tags=['roles'])
