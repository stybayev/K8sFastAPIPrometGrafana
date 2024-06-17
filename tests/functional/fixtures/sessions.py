import asyncio

import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(name='session_client', scope='session')
async def session_client() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
