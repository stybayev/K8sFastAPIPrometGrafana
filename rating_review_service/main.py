from fastapi.responses import ORJSONResponse
from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from rating_review_service.core.config import settings
from rating_review_service.models.post import Post
from rating_review_service.utils.enums import ShardedCollections
from rating_review_service.utils.wait_for_mongo_ready import wait_for_mongo_ready
from enum import Enum


async def enable_sharding() -> None:
    """
    Функция для шардирования базы данных.
    """
    client = AsyncIOMotorClient(settings.db.url)
    await client.admin.command("enableSharding", settings.db.default_database)


async def shard_collections(collections: Enum):
    """
    Функция шардирования коллекций MongoDB на основе перечисления Enum.

    :param collections: Enum, где каждый элемент содержит имя коллекции и ключ шардирования.
    """
    client = AsyncIOMotorClient(settings.db.url)
    db = client[settings.db.default_database]

    for collection in collections:
        collection_names = await db.list_collection_names()
        if collection.collection_name not in collection_names:
            await db.create_collection(collection.collection_name)

        shard_key = collection.shard_key
        await client.admin.command(
            "shardCollection",
            f"{settings.db.default_database}.{collection.collection_name}",
            key=shard_key
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    await wait_for_mongo_ready(settings.db.url)
    client = AsyncIOMotorClient(settings.db.url)

    await enable_sharding()
    await shard_collections(ShardedCollections)

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
