from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from auth.core.config import settings
from auth.db.postgres import create_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_database()
    yield


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/auth/openapi",
    openapi_url="/api/auth/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
