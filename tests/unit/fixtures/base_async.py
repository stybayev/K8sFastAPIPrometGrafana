import asyncio
import pytest_asyncio
import pytest


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'
