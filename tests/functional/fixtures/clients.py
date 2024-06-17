import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio.client import Redis

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client() -> AsyncElasticsearch:
    es_client = AsyncElasticsearch(
        hosts=test_settings.es_host,
        verify_certs=False
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    client = Redis(host=test_settings.redis_host,
                   port=test_settings.redis_port,
                   decode_responses=True)
    yield client
    await client.flushdb()
    await client.close()
