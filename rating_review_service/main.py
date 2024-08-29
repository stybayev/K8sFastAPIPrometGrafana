import asyncio
from fastapi.responses import ORJSONResponse
from rating_review_service.core.config import settings
from contextlib import asynccontextmanager
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from rating_review_service.models.post import Post
from rating_review_service.utils.wait_for_mongo_ready import wait_for_mongo_ready


@asynccontextmanager
async def lifespan(_: FastAPI):
    await wait_for_mongo_ready(settings.db.url)
    client = AsyncIOMotorClient(settings.db.url)
    await init_beanie(client[settings.db.default_database], document_models=[Post])
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
