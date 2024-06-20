import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import uuid


@pytest_asyncio.fixture(name='mock_db_session', scope='session')
async def fixture_mock_db_session():
    """
    Фикстура для создания мока асинхронной сессии базы данных.
    """
    session = MagicMock(spec=AsyncSession)
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda x: setattr(x, "id", uuid.uuid4()))
    session.execute = AsyncMock()
    yield session
    await session.close()
