import uuid
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError
from auth.models.users import User
from fastapi import status
from werkzeug.security import generate_password_hash
from redis.asyncio import Redis

from auth.services.users import UserService


@pytest.mark.anyio
async def test_register_user_success(auth_async_client: AsyncClient, mock_db_session,
                                     auth_override_dependencies):
    user_data = {
        'login': 'testuser',
        'password': 'testpassword',
        'first_name': 'Test',
        'last_name': 'User'
    }

    response = await auth_async_client.post('/users/', json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data['login'] == user_data["login"]
    assert data['first_name'] == user_data['first_name']
    assert data['last_name'] == user_data['last_name']


@pytest.mark.anyio
async def test_register_user_already_registered(auth_async_client: AsyncClient, mock_db_session,
                                                auth_override_dependencies):
    user_data = {
        'login': 'existinguser',
        'password': 'password123',
        'first_name': 'Existing',
        'last_name': 'User'
    }

    # Сначала создаем пользователя в базе данных
    existing_user = User(
        login=user_data['login'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )
    mock_db_session.add(existing_user)
    await mock_db_session.commit()

    # Настраиваем mock для возврата ошибки уникальности
    mock_db_session.commit.side_effect = IntegrityError(statement='', params={}, orig=None)

    # Пытаемся зарегистрировать того же пользователя снова
    response = await auth_async_client.post('/users/', json=user_data)
    assert response.status_code == 400

    data = response.json()
    assert data['detail'] == 'Login already registered'

    # Сбрасываем side_effect после теста
    mock_db_session.commit.side_effect = None


@pytest.mark.anyio
async def test_login_user_success(auth_async_client: AsyncClient,
                                  mock_db_session, auth_override_dependencies,
                                  authjwt):
    user_data = {
        'login': 'testuser',
        'password': 'testpassword'
    }

    # Мок для пользователя
    mock_user = User(
        login=user_data['login'],
        password=generate_password_hash(user_data['password']),
        first_name='Test',
        last_name='User'
    )

    # Мокаем методы UserService
    with patch.object(UserService, 'get_by_login', return_value=mock_user), \
            patch.object(User, 'check_password', return_value=True), \
            patch.object(UserService, 'get_user_roles', return_value=['user']):
        response = await auth_async_client.post('/users/login', json=user_data)

        assert response.status_code == 200

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data



