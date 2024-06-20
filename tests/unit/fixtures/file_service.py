from file_api.services.files import FileService
from file_api.db.db import get_db_session
from file_api.db.minio import get_minio
import pytest_asyncio
from httpx import AsyncClient
from file_api.main import app as file_api_app
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile


@pytest_asyncio.fixture(name='file_service')
def fixture_file_service(mock_minio_client, mock_db_session):
    """
    Фикстура для инициализации сервиса файлов с моками MinIO клиента и базы данных.
    """
    return FileService(mock_minio_client, mock_db_session)


@pytest_asyncio.fixture(name='file_api_async_client', scope='session')
async def fixture_file_async_client():
    """
    Фикстура для создания клиента AsyncClient.
    """
    async with AsyncClient(app=file_api_app, base_url='http://localhost/api/v1/files') as client:
        yield client


@pytest.fixture(name='file_api_override_dependencies', scope='session')
def fixture_file_override_dependencies(mock_db_session, mock_minio_client):
    file_api_app.dependency_overrides[get_db_session] = lambda: mock_db_session
    file_api_app.dependency_overrides[get_minio] = lambda: mock_minio_client
    yield
    file_api_app.dependency_overrides = {}


@pytest.fixture(name='test_file')
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
