import pytest_asyncio
from httpx import AsyncClient
from auth.services.users import UserService
from auth.db.postgres import get_db_session
from auth.main import app as auth_app


@pytest_asyncio.fixture(name='user_service')
def fixture_user_service(mock_db_session):
    """
    Фикстура для инициализации сервиса пользователей с моком базы данных.
    """
    return UserService(mock_db_session)


@pytest_asyncio.fixture(name='auth_async_client', scope='session')
async def fixture_auth_async_client():
    """
    Фикстура для создания клиента AsyncClient.
    """
    async with AsyncClient(app=auth_app, base_url='http://localhost/api/v1/auth') as client:
        yield client


@pytest_asyncio.fixture(name='auth_override_dependencies', scope='session')
def fixture_auth_override_dependencies(mock_db_session):
    auth_app.dependency_overrides[get_db_session] = lambda: mock_db_session
    yield
    auth_app.dependency_overrides = {}
