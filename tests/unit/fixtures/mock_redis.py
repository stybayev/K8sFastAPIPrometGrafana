import pytest_asyncio
from unittest.mock import AsyncMock

from redis.asyncio import Redis


@pytest_asyncio.fixture(scope='session')
async def mock_redis_client():
    client = AsyncMock(spec=Redis)
    client.set = AsyncMock()
    client.get = AsyncMock()
    client.flushdb = AsyncMock()
    client.close = AsyncMock()
    yield client
    await client.flushdb()
    await client.close()
