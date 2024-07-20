from fastapi import APIRouter, Depends, Request
from fastapi_jwt_auth import AuthJWT

from auth.core.jwt import security_jwt
from auth.services.oauth_service import OAuthService, get_oauth_service

router = APIRouter()


@router.get("/yandex/login")
async def yandex_login(service: OAuthService = Depends(get_oauth_service)):
    """
    Роут для перенаправления пользователя на сайт Яндекса для авторизации
    """
    return await service.yandex_login()


@router.get("/yandex/callback")
async def yandex_callback(
        request: Request,
        Authorize: AuthJWT = Depends(),
        service: OAuthService = Depends(get_oauth_service)
):
    """
    Роут для обработки кода авторизации Яндекса, получения токена доступа и информации о пользователе
    """
    code = request.query_params.get("code")
    return await service.yandex_callback(code, Authorize)


@router.delete("/yandex/unlink")
async def unlink_yandex_account(
        user: dict = Depends(security_jwt),
        Authorize: AuthJWT = Depends(),
        service: OAuthService = Depends(get_oauth_service)
):
    """
    Роут для открепления аккаунта Яндекса от пользователя.
    """
    Authorize.jwt_required()

    current_user_id = Authorize.get_jwt_subject()
    return await service.unlink_social_account(user_id=current_user_id, social_name="yandex")
