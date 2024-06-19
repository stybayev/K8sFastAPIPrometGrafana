import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(name='mock_db_session', scope='session')
async def fixture_mock_db_session():
    """
    Фикстура для создания мока асинхронной сессии базы данных.
    """
    session = MagicMock(spec=AsyncSession)
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    yield session
    await session.close()
