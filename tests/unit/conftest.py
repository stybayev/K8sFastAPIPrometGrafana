import asyncio
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from file_api.db.db import get_db_session
from file_api.db.minio import set_minio, close_minio, get_minio
from file_api.main import app
from file_api.services.files import FileService
from miniopy_async import Minio
from httpx import AsyncClient
import pytest


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'


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


@pytest_asyncio.fixture(name='file_service')
def fixture_file_service(mock_minio_client, mock_db_session):
    """
    Фикстура для инициализации сервиса файлов с моками MinIO клиента и базы данных.
    """
    return FileService(mock_minio_client, mock_db_session)


@pytest_asyncio.fixture(name='test_file')
def fixture_test_file():
    """
    Фикстура для создания мока файла для тестирования.
    """
    file = MagicMock(spec=UploadFile)
    file.filename = 'test.txt'
    file.content_type = 'text/plain'
    file.read = AsyncMock(return_value=b"test content")
    file.seek = AsyncMock()
    file.file = MagicMock()
    return file


@pytest_asyncio.fixture(name='async_client', scope='session')
async def fixture_async_client():
    """
    Фикстура для создания клиента AsyncClient.
    """
    async with AsyncClient(app=app, base_url='http://localhost/api/v1/files') as client:
        yield client


@pytest_asyncio.fixture(name='override_dependencies', scope='session')
def fixture_override_dependencies(mock_db_session, mock_minio_client):
    app.dependency_overrides[get_db_session] = lambda: mock_db_session
    app.dependency_overrides[get_minio] = lambda: mock_minio_client
    yield
    app.dependency_overrides = {}
