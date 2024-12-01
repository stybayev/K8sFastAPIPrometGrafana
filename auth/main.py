import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from auth.api.v1 import oauth_router, roles, users
from auth.core.config import settings
from auth.core.jwt import JWTSettings
from auth.core.middleware import before_request, check_blacklist
from auth.core.tracer import init_tracer
from auth.db import redis
from auth.utils.exception_handlers import authjwt_exception_handler
from auth.utils.sentry_hook import before_send
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn=os.getenv("AUTH_SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    send_default_pii=True,  # Включает передачу данных о пользователе
    before_send=before_send,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    AuthJWT.load_config(lambda: JWTSettings())
    redis.connection = Redis(host=settings.redis_host, port=settings.redis_port)

    yield

    await redis.connection.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/auth/openapi",
    openapi_url="/api/auth/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/api/v1/auth/users/login",
)

if settings.enable_tracing:
    init_tracer(app)
    FastAPIInstrumentor.instrument_app(app)

app.add_exception_handler(AuthJWTException, authjwt_exception_handler)

app.middleware("http")(before_request)
app.middleware("http")(check_blacklist)

Instrumentator().instrument(app).expose(app)

app.include_router(users.router, prefix="/api/v1/auth/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/auth/roles", tags=["roles"])
app.include_router(oauth_router.router, prefix="/api/v1/auth", tags=["yandex"])
