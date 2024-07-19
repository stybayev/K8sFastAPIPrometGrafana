import logging
import uuid
from unittest.mock import patch

import pytest

from auth.models.users import Role
from auth.schema.roles import UserPermissionsSchema
from auth.services.roles import RoleService


@pytest.mark.asyncio
async def test_create_role(setup_jwt, test_role, auth_async_client,
                           mock_redis_client, request_headers):
    role_data = {
        "name": "test_role",
        "description": "test description",
        "permissions": ["test_permission"]
    }
    headers = {
        "Authorization": f"Bearer {setup_jwt['access_token']}",
        "X-Refresh-Token": setup_jwt['refresh_token'],
        'X-Request-Id': str(uuid.uuid4())
    }

    # Проверяем случай, когда роль ещё не создана
    with (patch('auth.core.middleware.redis_client', mock_redis_client),
          patch.object(RoleService, "is_exist", return_value=False),
          patch.object(RoleService, "is_admin", return_value=True)):
        mock_redis_client.get.return_value = None  # или "blacklisted" для проверки черного списка
        response = await auth_async_client.post("/roles/", json=role_data, headers=headers)
        assert response.status_code == 200

    # Проверяем случай, когда роль существует
    with (patch('auth.core.middleware.redis_client', mock_redis_client),
          patch.object(RoleService, "is_exist", return_value=True),
          patch.object(RoleService, "is_admin", return_value=True)):
        mock_redis_client.get.return_value = None
        response = await auth_async_client.post("/roles/", json=role_data, headers=headers)
        assert response.status_code == 400  # проверяем правильность обработки черного списка

    # Проверяем случай, когда пользователь не админ
    with (patch('auth.core.middleware.redis_client', mock_redis_client),
          patch.object(RoleService, "is_exist", return_value=True),
          patch.object(RoleService, "is_admin", return_value=False)):
        mock_redis_client.get.return_value = None
        response = await auth_async_client.post("/roles/", json=role_data, headers=headers)
        assert response.status_code == 403

    # Проверяем случай, когда токен в черном списке
    with (patch('auth.core.middleware.redis_client', mock_redis_client),
          patch.object(RoleService, "is_exist", return_value=True),
          patch.object(RoleService, "is_admin", return_value=False)):
        mock_redis_client.get.return_value = "blacklisted"
        response = await auth_async_client.post("/roles/", json=role_data, headers=headers)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_role(setup_jwt, test_role, auth_async_client, mock_redis_client, mock_db_session):
    role_data = {
        "role_name": "test_role"
    }
    headers = {
        "Authorization": f"Bearer {setup_jwt['access_token']}",
        "X-Refresh-Token": setup_jwt['refresh_token'],
        'X-Request-Id': str(uuid.uuid4())
    }

    role_id = uuid.uuid4()
    mock_role = Role(name='test_role', description='Test Role')
    mock_role.id = role_id

    mock_response = {"message": f"Role '{role_data['role_name']}' deleted successfully"}

    with (
        patch('auth.core.middleware.redis_client', mock_redis_client),
        patch('auth.core.middleware.check_blacklist', None),
        patch.object(RoleService, "is_admin", return_value=True),
        patch.object(RoleService, "delete_role", return_value=mock_response)
    ):
        mock_redis_client.get.return_value = None

        response = await auth_async_client.delete("/roles/", params=role_data, headers=headers)
        logging.info(response.json())
        assert response.status_code == 200
        assert response.json() == mock_response
        mock_db_session.commit.side_effect = None


@pytest.mark.anyio
async def test_update_role(setup_jwt, test_role, auth_async_client, mock_redis_client, mock_db_session):
    update_role_data = {
        "role_name": "update_test_role"
    }
    headers = {
        "Authorization": f"Bearer {setup_jwt['access_token']}",
        "X-Refresh-Token": setup_jwt['refresh_token'],
        'X-Request-Id': str(uuid.uuid4())
    }

    role = Role(name='test_role', description='Test Role')
    mock_db_session.add(role)
    await mock_db_session.commit()
    await mock_db_session.refresh(role)

    with (
        patch('auth.core.middleware.redis_client', mock_redis_client),
        patch('auth.core.middleware.check_blacklist', None),
        patch.object(RoleService, "is_admin", return_value=True),
        patch.object(RoleService, "update_role", return_value=role)
    ):
        mock_redis_client.get.return_value = None

        response = await auth_async_client.patch(f"/roles/{role.id}", json=update_role_data, headers=headers)
        assert response.status_code == 200


@pytest.mark.anyio
async def test_get_user_permissions(setup_jwt, test_role, auth_async_client, mock_redis_client, mock_db_session):

    user_id = uuid.uuid4()
    mock_response = UserPermissionsSchema(
        user_id=user_id,
        permissions=[
            "test1", "test2"
        ]
    )
    headers = {
        "Authorization": f"Bearer {setup_jwt['access_token']}",
        "X-Refresh-Token": setup_jwt['refresh_token'],
        'X-Request-Id': str(uuid.uuid4())
    }

    with (
        patch('auth.core.middleware.redis_client', mock_redis_client),
        patch('auth.core.middleware.check_blacklist', None),
        patch.object(RoleService, "is_admin", return_value=True),
        patch.object(RoleService, "get_user_permissions", return_value=mock_response)
    ):
        mock_redis_client.get.return_value = None

        response = await auth_async_client.get(f"/roles/users/{user_id}/permissions", headers=headers)
        assert response.status_code == 200