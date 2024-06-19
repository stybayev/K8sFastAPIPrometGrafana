from sqlalchemy.future import select
from file_api.models.files import FileDbModel
from unittest.mock import AsyncMock, MagicMock
from aiohttp import ClientResponse, StreamReader
from starlette.responses import StreamingResponse

from file_api.utils.exceptions import NotFoundException
from fastapi import status
import pytest


@pytest.mark.anyio
async def test_download_file_success(mock_db_session, mock_minio_client,
                                     file_api_async_client, file_api_override_dependencies):
    short_name = 'short_name_123'
    path_in_storage = 'test/path'
    filename = 'test.txt'
    content = b'test content'

    mock_file_record = FileDbModel(
        path_in_storage=path_in_storage,
        filename=filename,
        short_name=short_name,
        size=123,
        file_type='text/plain'
    )
    mock_db_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=mock_file_record)

    async def mock_iter_chunked(chunk_size):
        yield content

    mock_response = MagicMock(ClientResponse)
    mock_response.content = MagicMock(StreamReader)
    mock_response.content.iter_chunked = mock_iter_chunked
    mock_minio_client.get_object.return_value = mock_response

    response = await file_api_async_client.get(f'/download/{short_name}')
    response_content = await response.aread()

    assert response.status_code == status.HTTP_200_OK
    assert response_content == content
    assert response.headers['content-disposition'] == f"attachment; filename*=UTF-8''{filename}"


@pytest.mark.anyio
async def test_download_file_not_found(mock_db_session, file_api_async_client, file_api_override_dependencies):
    short_name = 'short_name_123'

    mock_db_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    response = await file_api_async_client.get(f'/download/{short_name}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'File not found'}


@pytest.mark.anyio
async def test_get_presigned_url_success(mock_db_session, mock_minio_client,
                                         file_api_async_client, file_api_override_dependencies):
    """
    Тест успешного получения подписанной ссылки.
    """
    short_name = 'short_name_123'
    path_in_storage = 'test/path'
    mock_presigned_url = 'http://presigned.url'

    mock_file_record = FileDbModel(
        path_in_storage=path_in_storage,
        filename='test.txt',
        short_name=short_name,
        size=123,
        file_type='text/plain'
    )

    mock_db_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=mock_file_record)
    mock_minio_client.get_presigned_url.return_value = mock_presigned_url

    response = await file_api_async_client.get(f'/presigned-url/{short_name}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_presigned_url


@pytest.mark.anyio
async def test_get_presigned_url_not_found(mock_db_session, file_api_async_client, file_api_override_dependencies):
    """
    Тест получения ошибки 404 при попытке получить подписанную ссылку для несуществующего файла.
    """
    short_name = 'short_name_123'

    mock_db_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    response = await file_api_async_client.get(f'/presigned-url/{short_name}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'File not found'}


@pytest.mark.anyio
async def test_save_file(file_service, test_file):
    """
    Тест сохранения файла
    """
    path = 'test/path'
    file_record = await file_service.save(test_file, path)

    assert file_record.filename == test_file.filename
    assert file_record.file_type == test_file.content_type
    assert file_record.size == len(b"test content")
    assert file_record.path_in_storage == path


@pytest.mark.anyio
async def test_get_file_record_success(file_service, mock_db_session):
    """
    Тест успешного получения записи файла по короткому имени.
    """
    short_name = 'short_name_123'
    mock_file_record = FileDbModel(
        path_in_storage='test/path',
        filename='test.txt',
        short_name=short_name,
        size=123,
        file_type='text/plain',
    )

    # Настраиваем mock на возврат записи файла
    mock_db_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=mock_file_record)

    # Сравнение вызова get_file_record
    file_record = await file_service.get_file_record(short_name)
    assert file_record == mock_file_record


@pytest.mark.anyio
async def test_get_file_record_not_found(file_service, mock_db_session):
    """
    Тест ситуации, когда запись файла не найдена по короткому имени.
    """
    short_name = 'short_name_123'

    mock_db_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    with pytest.raises(NotFoundException) as exc_info:
        await file_service.get_file_record(short_name)

    assert exc_info.value.detail == 'File not found'


@pytest.mark.anyio
async def test_get_file(file_service, mock_minio_client):
    """
    Тест успешного получения файла из Minio.
    """
    path = 'test/path'
    filename = 'test.txt'
    content = b"test content"

    # Создаем mock ответа Minio get_object
    mock_response = MagicMock(ClientResponse)
    mock_response.content = MagicMock(StreamReader)
    mock_response.content.iter_chunked = AsyncMock(return_value=[content])
    mock_minio_client.get_object.return_value = mock_response

    response = await file_service.get_file(path, filename)
    assert isinstance(response, StreamingResponse)


@pytest.mark.anyio
async def test_get_presigned_url(file_service, mock_db_session, mock_minio_client):
    """
    Тест успешного получения подписанной ссылки.
    """
    short_name = 'short_name_123'

    # Настраиваем mock на возврат записи файла
    mock_presigned_url = 'http://presigned.url'
    mock_minio_client.get_presigned_url.return_value = mock_presigned_url

    # Сравнение вызова get_presigned_url
    presigned_url = await file_service.get_presigned_url(short_name)
    assert presigned_url == mock_presigned_url
