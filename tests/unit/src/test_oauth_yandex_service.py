import pytest
from fastapi import status, HTTPException
from httpx import AsyncClient
from unittest.mock import patch
from auth.services.oauth_service import OAuthService


@pytest.mark.anyio
async def test_yandex_callback_success(auth_async_client: AsyncClient, mock_db_session, request_headers):
    """
    Проверяем, что при успешном входе возвращается access_token и refresh_token
    """
    code = "valid_code"

    with (
        patch.object(OAuthService, 'get_yandex_token', return_value={"access_token": "valid_token"}),
        patch.object(OAuthService, 'get_yandex_user_info', return_value={
            "id": "user_id",
            "default_email": "user@example.com",
            "login": "user_login",
            "first_name": "First",
            "last_name": "Last"
        }),
        patch.object(OAuthService, 'get_or_create_user', return_value={"id": "user_id"}),
        patch.object(OAuthService, 'generate_tokens_for_user', return_value={
            "access_token": "access_token",
            "refresh_token": "refresh_token"
        })
    ):
        response = await auth_async_client.get(f'/yandex/callback?code={code}', headers=request_headers)
        assert response.status_code == 200

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data


@pytest.mark.anyio
async def test_yandex_callback_missing_code(auth_async_client: AsyncClient, request_headers):
    """
    Проверяем, что при отсутствии кода возвращается ошибка
    """
    response = await auth_async_client.get('/yandex/callback', headers=request_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()
    assert data['detail'] == 'Authorization code not provided'


@pytest.mark.anyio
async def test_unlink_yandex_account_success(auth_async_client: AsyncClient, mock_db_session, request_headers):
    """
    Проверяем, что при успешном откреплении аккаунта возвращается статус 200
    """
    with (patch.object(OAuthService, 'unlink_social_account',
                       return_value={"detail": "Social account unlinked successfully"})):
        response = await auth_async_client.delete('/yandex/unlink', headers=request_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['detail'] == 'Social account unlinked successfully'


@pytest.mark.anyio
async def test_unlink_yandex_account_not_found(auth_async_client: AsyncClient, mock_db_session, request_headers):
    """
    Проверяем, что при отсутствии социального аккаунта возвращается статус 404
    """
    with (patch.object(OAuthService, 'unlink_social_account',
                       side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                                 detail="Social account not found"))):
        response = await auth_async_client.delete('/yandex/unlink', headers=request_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()
        assert data['detail'] == 'Social account not found'
