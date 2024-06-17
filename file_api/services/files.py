import logging
import urllib
from datetime import timedelta
from functools import lru_cache
from aiohttp import ClientSession
from fastapi import UploadFile, Depends, HTTPException
from miniopy_async import Minio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import StreamingResponse
from file_api.core.config import settings
from file_api.db.db import get_db_session
from file_api.db.minio import get_minio
from file_api.models.files import FileDbModel
from shortuuid import uuid as shortuuid

from file_api.utils.exceptions import NotFoundException


class FileService:
    def __init__(self, minio: Minio, db_session: AsyncSession) -> None:
        self.client = minio
        self.db_session = db_session

    async def save(self, file: UploadFile, path: str) -> FileDbModel:
        # Получаем размер файла для поля size
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)

        # Определяем значение поля short_name
        short_name = shortuuid()

        # Загружаем файл в Minio
        await self.client.put_object(
            bucket_name=settings.backet_name, object_name=path,
            data=file.file, length=file_size,
            part_size=10 * 1024 * 1024,
        )

        # Сохраняем информацию о файле в базу данных
        new_file = FileDbModel(
            path_in_storage=path,
            filename=file.filename,
            short_name=short_name,
            size=file_size,
            file_type=file.content_type,
        )
        self.db_session.add(new_file)
        await self.db_session.commit()
        await self.db_session.refresh(new_file)
        return new_file

    async def get_file_record(self, short_name: str) -> FileDbModel:
        file_record = await self.db_session.execute(
            select(FileDbModel).where(FileDbModel.short_name == short_name)
        )
        file_record = file_record.scalar_one_or_none()
        if not file_record:
            raise NotFoundException(detail='File not found')
        return file_record

    async def get_file(self, path: str, filename: str) -> StreamingResponse:
        async def file_stream():
            try:
                async with ClientSession() as session:
                    result = await self.client.get_object(settings.backet_name, path, session=session)
                    async for chunk in result.content.iter_chunked(32 * 1024):
                        yield chunk
            except Exception as e:
                logging.error(f'Failed to download file: {e}')
                return

        encoded_filename = urllib.parse.quote(filename)

        return StreamingResponse(
            file_stream(),
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    async def get_presigned_url(self, path: str) -> str:
        return await self.client.get_presigned_url('GET', settings.backet_name, path, expires=timedelta(days=1), )


@lru_cache()
def get_file_service(minio: Minio = Depends(get_minio),
                     db_session: AsyncSession = Depends(get_db_session)) -> FileService:
    return FileService(minio, db_session)
