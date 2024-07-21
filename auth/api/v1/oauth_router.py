from fastapi import APIRouter, Depends, Request
from fastapi_jwt_auth import AuthJWT

from auth.core.jwt import security_jwt
from auth.services.oauth_service import OAuthService, get_oauth_service
from auth.utils.enums import AuthProvider

router = APIRouter()


@router.get("/{provider}/login")
async def login(
    provider: AuthProvider,
    service: OAuthService = Depends(get_oauth_service),
):
    """
    Роут для перенаправления пользователя на сайт провайдера для авторизации
    """
    return await service.login(provider)


@router.get("/{provider}/callback")
async def callback(
    provider: AuthProvider,
    request: Request,
    Authorize: AuthJWT = Depends(),
    service: OAuthService = Depends(get_oauth_service),
):
    """
    Роут для обработки кода авторизации провайдера, получения токена доступа и информации о пользователе
    """
    code = request.query_params.get("code")
    return await service.callback(provider, code, Authorize)


@router.delete("/{provider}/unlink")
async def unlink_account(
    provider: AuthProvider,
    user: dict = Depends(security_jwt),
    Authorize: AuthJWT = Depends(),
    service: OAuthService = Depends(get_oauth_service),
):
    """
    Роут для открепления аккаунта провайдера от пользователя.
    """
    current_user_id = Authorize.get_jwt_subject()
    return await service.unlink_social_account(
        user_id=current_user_id, social_name=provider
    )
