from http import HTTPStatus

from fastapi import APIRouter, UploadFile, HTTPException, Depends
from starlette.responses import StreamingResponse

from file_api.schemas.files import FileResponse
from file_api.services.files import FileService, get_file_service
from file_api.utils.exceptions import NotFoundException

router = APIRouter()


@router.post("/upload/", response_model=FileResponse)
async def upload_file(file: UploadFile,
                      path: str,
                      service: FileService = Depends(get_file_service)):
    """
    ## Загрузка файла

    Этот эндпоинт позволяет загрузить файл в указанный S3 бакет и путь. Файл сохраняется в хранилище MinIO,
    а метаданные файла сохраняются в базе данных PostgreSQL.

    ### Параметры:
    - **file**: Загружаемый файл.
    - **path**: Путь внутри бакета, по которому будет сохранен файл.

    ### Возвращает:
      - `id`: Уникальный идентификатор файла.
      - `path_in_storage`: Полный путь к файлу в хранилище.
      - `filename`: Оригинальное имя файла.
      - `size`: Размер файла в байтах.
      - `file_type`: MIME-тип файла.
      - `short_name`: Короткое, уникальное имя файла.
      - `created`: Временная метка создания файла.
    """
    try:
        file_record = await service.save(file, path)
        return FileResponse(
            id=file_record.id,
            path_in_storage=file_record.path_in_storage,
            filename=file_record.filename,
            size=file_record.size,
            file_type=file_record.file_type,
            short_name=file_record.short_name,
            created=file_record.created
        )
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/download/{short_name}", response_class=StreamingResponse)
async def download_file(short_name: str, service: FileService = Depends(get_file_service)):
    """
    ## Скачать файл

    Этот эндпоинт позволяет скачать файл из S3 хранилища по его короткому имени.

    ### Параметры:
    - **short_name**: Короткое имя файла, по которому будет произведен поиск файла в базе данных и S3 хранилище.

    ### Возвращает:
      - Файл в виде StreamingResponse.
    """
    try:
        file_record = await service.get_file_record(short_name)
        return await service.get_file(file_record.path_in_storage, file_record.filename)
    except NotFoundException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/presigned-url/{short_name}")
async def get_presigned_url(short_name: str, service: FileService = Depends(get_file_service)):
    """
    ## Получить подписанную ссылку

    Этот эндпоинт позволяет получить подписанную ссылку для скачивания файла из S3 хранилища по его короткому имени.

    ### Параметры:
    - **short_name**: Короткое имя файла, по которому будет произведен поиск файла в базе данных и S3 хранилище.

    ### Возвращает:
      - Подписанную ссылку для скачивания файла.
    """
    try:
        file_record = await service.get_file_record(short_name)
        return await service.get_presigned_url(file_record.path_in_storage)
    except NotFoundException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
