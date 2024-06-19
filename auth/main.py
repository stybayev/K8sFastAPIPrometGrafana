from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from auth.core.config import settings
from auth.db.postgres import create_database
from auth.db.redis import redis
from auth.api.v1 import users, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)

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

app.include_router(users.router, prefix="/api/v1/auth/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/auth/roles", tags=["roles"])
