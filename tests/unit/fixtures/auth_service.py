import os

# Отключаем трассировку для тестов до загрузки приложения
os.environ["ENABLE_TRACING"] = "false"

import pytest_asyncio
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient

from auth.core.jwt import security_jwt
from auth.db.postgres import get_db_session
from auth.db.redis import get_redis
from auth.main import app as auth_app
from auth.models.users import User
from auth.services.users import UserService
from tests.unit.settings import TestJWTSettings
import uuid


@pytest_asyncio.fixture(name='user_service')
def fixture_user_service(mock_db_session, mock_redis_client):
    """
    Фикстура для инициализации сервиса пользователей с моком базы данных.
    """
    return UserService(mock_db_session, mock_redis_client)


@pytest_asyncio.fixture(name='auth_async_client', scope='session')
async def fixture_auth_async_client(auth_override_dependencies):
    """
    Фикстура для создания клиента AsyncClient.
    """
    async with AsyncClient(app=auth_app, base_url='http://127.0.0.1/api/v1/auth/') as client:
        yield client


@pytest_asyncio.fixture(scope='session')
def authjwt():
    AuthJWT.load_config(lambda: TestJWTSettings())
    return AuthJWT()


@pytest_asyncio.fixture(name='auth_override_dependencies', scope='session')
def fixture_auth_override_dependencies(mock_db_session, mock_redis_client, authjwt):
    auth_app.dependency_overrides[get_db_session] = lambda: mock_db_session
    auth_app.dependency_overrides[get_redis] = lambda: mock_redis_client
    auth_app.dependency_overrides[AuthJWT] = lambda: authjwt
    auth_app.dependency_overrides[security_jwt] = lambda: {"id": "test_user_id", "roles": ["user"]}

    yield
    auth_app.dependency_overrides = {}


@pytest_asyncio.fixture(name='test_user')
def fixture_test_user():
    """
    Фикстура для создания мока пользователя для тестирования.
    """
    return {
        "login": "test_user",
        "password": "test_password",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest_asyncio.fixture(name='existing_user', scope='function')
async def fixture_existing_user(mock_db_session, test_user: dict):
    """
    Фикстура для создания существующего пользователя в базе данных.
    """
    user = User(
        login=test_user["login"],
        password=test_user["password"],
        first_name=test_user["first_name"],
        last_name=test_user["last_name"],
        email=test_user["login"] + "@example.com"
    )
    mock_db_session.add(user)
    await mock_db_session.commit()
    await mock_db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope='function')
def request_headers():
    return {
        'X-Request-Id': str(uuid.uuid4())
    }
