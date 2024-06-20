import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from miniopy_async import Minio
from file_api.db.minio import set_minio, close_minio


@pytest_asyncio.fixture(name='mock_minio_client', scope='session')
async def fixture_mock_minio_client():
    """
    Фикстура для создания мока MinIO клиента.
    """
    client = MagicMock(spec=Minio)
    client.put_object = AsyncMock()
    client.get_object = AsyncMock()
    client.get_presigned_url = AsyncMock()
    client.close = AsyncMock()
    set_minio(client)
    yield client
    await client.close()
    await close_minio()
