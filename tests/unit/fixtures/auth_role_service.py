import os

# Отключаем трассировку для тестов до загрузки приложения
os.environ["ENABLE_TRACING"] = "false"

import pytest_asyncio
from fastapi_jwt_auth import AuthJWT

from auth.core.jwt import JWTSettings
from auth.models.users import Role
import uuid

@pytest_asyncio.fixture
def setup_jwt():
    @AuthJWT.load_config
    def get_config():
        return JWTSettings()

    jwt = AuthJWT()
    access_token = jwt.create_access_token(subject="testuser", user_claims={"jti": "access_test_jti"})
    refresh_token = jwt.create_refresh_token(subject="testuser", user_claims={"jti": "refresh_test_jti"})
    return {"access_token": access_token, "refresh_token": refresh_token}


@pytest_asyncio.fixture(name='test_role')
def role_test():
    return {
        "name": "test_role",
        "description": "test description",
        "permissions": ["test_permission"]
    }


@pytest_asyncio.fixture(name='existing_role', scope='function')
async def fixture_existing_role(mock_db_session, test_user: dict):
    role = Role(**test_role)
    mock_db_session.add(role)
    await mock_db_session.commit()
    await mock_db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope='function')
def request_headers():
    return {
        'X-Request-Id': str(uuid.uuid4())
    }