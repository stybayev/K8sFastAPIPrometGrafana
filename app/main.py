import uvicorn
import logging

from elasticsearch import AsyncElasticsearch
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from app.api.v1 import films, genres, persons
from app.core.config import settings
from app.db import elastic, redis
from app.dependencies.main import setup_dependencies


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

setup_dependencies(app)
