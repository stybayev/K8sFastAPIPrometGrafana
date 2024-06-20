import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError
from auth.models.users import User


@pytest.mark.anyio
async def test_register_user_success(auth_async_client: AsyncClient, mock_db_session,
                                     auth_override_dependencies):
    user_data = {
        'login': 'testuser',
        'password': 'testpassword',
        'first_name': 'Test',
        'last_name': 'User'
    }

    response = await auth_async_client.post('/users/users', json=user_data)
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
    response = await auth_async_client.post('/users/users', json=user_data)
    assert response.status_code == 400

    data = response.json()
    assert data['detail'] == 'Login already registered'

    # Сбрасываем side_effect после теста
    mock_db_session.commit.side_effect = None
