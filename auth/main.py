from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from auth.core.config import settings
from auth.db.postgres import create_database
from auth.db.redis import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)

    # TODO: создание БД надо будет переделать через alembic
    await create_database()

    yield

    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/auth/openapi",
    openapi_url="/api/auth/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
