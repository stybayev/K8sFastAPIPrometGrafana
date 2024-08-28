import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def wait_for_mongo_ready(uri: str, timeout: int = 60) -> None:
    """
    Функция ожидания готовности MongoDB
    """
    client = AsyncIOMotorClient(uri)
    end_time = asyncio.get_event_loop().time() + timeout
    while True:
        try:
            await client.admin.command('ping')
            break
        except Exception:
            if asyncio.get_event_loop().time() > end_time:
                raise RuntimeError("Timed out waiting for MongoDB to be ready")
            await asyncio.sleep(5)