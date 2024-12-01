import os
from contextlib import asynccontextmanager

import sentry_sdk
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis

from app.api.v1 import films, genres, persons
from app.core.config import settings
from app.db import elastic, redis
from app.dependencies.main import setup_dependencies
from app.utils.sentry_hook import before_send
from auth.core.jwt import JWTSettings
from auth.core.middleware import check_blacklist
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn=os.getenv("APP_SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    send_default_pii=True,  # Включает передачу данных о пользователе
    before_send=before_send,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    AuthJWT.load_config(lambda: JWTSettings())
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[f'http://{settings.elastic_host}:{settings.elastic_port}']
    )

    yield

    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/films/openapi",
    openapi_url="/api/films/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.middleware("http")(check_blacklist)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

Instrumentator().instrument(app).expose(app)

setup_dependencies(app)
