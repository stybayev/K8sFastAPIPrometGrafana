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
from auth.core.middleware import check_blacklist
from auth.db import redis
from auth.utils.exception_handlers import authjwt_exception_handler


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

app.add_exception_handler(AuthJWTException, authjwt_exception_handler)

app.middleware("http")(check_blacklist)

app.include_router(users.router, prefix='/api/v1/auth/users', tags=['users'])
app.include_router(roles.router, prefix='/api/v1/auth/roles', tags=['roles'])
