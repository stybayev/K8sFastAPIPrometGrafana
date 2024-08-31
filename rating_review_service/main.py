from fastapi.responses import ORJSONResponse
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rating_review_service.core.config import settings
from rating_review_service.db.mongo import shard_collections
from rating_review_service.utils.enums import ShardedCollections
from rating_review_service.utils.wait_for_mongo_ready import wait_for_mongo_ready


@asynccontextmanager
async def lifespan(_: FastAPI):
    await wait_for_mongo_ready(settings.db.url)
    await shard_collections(ShardedCollections)

    yield


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/rating/openapi",
    openapi_url="/api/rating/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

