from contextlib import asynccontextmanager
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from rating_review_service.core.config import settings
from enum import Enum

client = AsyncIOMotorClient(settings.db.url)
db = client[settings.db.default_database]


async def shard_collections(collections: Enum):
    """
    Функция шардирования и создания коллекций.
    """
    await client.admin.command("enableSharding", settings.db.default_database)

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


async def get_db() -> AsyncGenerator:
    try:
        yield db
    finally:
        pass
