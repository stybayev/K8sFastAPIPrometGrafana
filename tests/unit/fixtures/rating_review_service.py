import pytest_asyncio
from unittest.mock import AsyncMock
from motor.motor_asyncio import AsyncIOMotorDatabase
from httpx import AsyncClient

from rating_review_service.main import app as rating_app
from rating_review_service.services.review import ReviewService
from rating_review_service.db.mongo import get_db


@pytest_asyncio.fixture(scope='session')
async def mock_mongo_db():
    mock_db = AsyncMock(spec=AsyncIOMotorDatabase)
    yield mock_db


@pytest_asyncio.fixture(name='review_service', scope='function')
def fixture_review_service(mock_mongo_db):
    """
    Фикстура для инициализации сервиса рецензий с моком базы данных.
    """
    service = ReviewService(mock_mongo_db)
    return service


@pytest_asyncio.fixture(name='rating_review_async_client', scope='session')
async def fixture_rating_review_async_client(rating_review_override_dependencies):
    """
    Фикстура для создания клиента AsyncClient для сервиса рецензий.
    """
    async with AsyncClient(app=rating_app, base_url='http://0.0.0.0:8085/api/v1/reviews/') as client:
        yield client


@pytest_asyncio.fixture(name='rating_review_override_dependencies', scope='session')
def fixture_rating_review_override_dependencies(mock_mongo_db):
    rating_app.dependency_overrides[get_db] = lambda: mock_mongo_db
    yield
    rating_app.dependency_overrides = {}
