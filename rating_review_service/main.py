from fastapi.responses import ORJSONResponse

from rating_review_service.core.config import settings
from contextlib import asynccontextmanager
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from rating_review_service.models.post import Post


@asynccontextmanager
async def lifespan(_: FastAPI):
    client = AsyncIOMotorClient('mongodb://mongos1:27017')
    await init_beanie(database=client.db_name, document_models=[Post])
    yield
    client.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/rating/openapi",
    openapi_url="/api/rating/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.get("/")
async def read_root():
    await Post(subject='Тема сообщения', text='Текст сообщения').insert()
    return {"Hello": "World"}
