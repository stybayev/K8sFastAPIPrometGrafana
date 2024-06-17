from contextlib import asynccontextmanager
from miniopy_async import Minio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from file_api.api.v1 import files
from file_api.core.config import settings
from file_api.db.minio import set_minio, close_minio, create_bucket_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    minio_client = Minio(
        endpoint=settings.minio_host,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=False,
    )
    set_minio(minio_client)
    await create_bucket_if_not_exists(settings.backet_name)

    yield
    await close_minio()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/files/openapi",
    openapi_url="/api/files/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(files.router, prefix='/api/v1/files', tags=['files'])
