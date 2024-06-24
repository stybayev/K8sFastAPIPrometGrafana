from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError
from auth.models.users import User

from werkzeug.security import generate_password_hash

from auth.services.users import UserService
from fastapi import status
from fastapi_jwt_auth import AuthJWT


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
async def test_login_user_success(auth_async_client: AsyncClient):
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
    with (patch.object(UserService, 'get_by_login', return_value=mock_user),
          patch.object(User, 'check_password', return_value=True),
          patch.object(UserService, 'get_user_roles', return_value=['user'])):
        response = await auth_async_client.post('/users/login', json=user_data)

        assert response.status_code == 200

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data


@pytest.mark.anyio
async def test_login_user_invalid_credentials(auth_async_client: AsyncClient):
    user_data = {
        'login': 'wronguser',
        'password': 'wrongpassword'
    }

    # Мокаем методы UserService для возврата None при попытке найти пользователя по логину
    with (patch.object(UserService, 'get_by_login', return_value=None),
          patch.object(User, 'check_password', return_value=False)):
        response = await auth_async_client.post('/users/login', json=user_data)

        assert response.status_code == 401

        data = response.json()
        assert data['detail'] == 'Invalid login or password'


@pytest.mark.anyio
async def test_update_user_credentials_success(auth_async_client: AsyncClient, existing_user: User):
    update_data = {
        'login': 'new_login',
        'password': 'new_password'
    }

    updated_user = User(
        login=update_data['login'],
        password=generate_password_hash(update_data['password']),
        first_name=existing_user.first_name,
        last_name=existing_user.last_name
    )
    # Устанавливаем id после создания объекта
    updated_user.id = existing_user.id

    # Мокаем методы AuthJWT и UserService
    with (patch.object(AuthJWT, 'jwt_required', return_value=None),
          patch.object(AuthJWT, 'get_jwt_subject', return_value=str(existing_user.id)),
          patch.object(UserService, 'update_user_credentials', return_value=updated_user)):
        response = await auth_async_client.patch('/users/update-credentials', json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data['id'] == str(existing_user.id)
        assert data['login'] == update_data["login"]
        assert data['first_name'] == existing_user.first_name
        assert data['last_name'] == existing_user.last_name


@pytest.mark.anyio
async def test_update_user_credentials_unauthorized(auth_async_client: AsyncClient):
    update_data = {
        'login': 'new_login',
        'password': 'new_password'
    }

    response = await auth_async_client.patch('/users/update-credentials', json=update_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED