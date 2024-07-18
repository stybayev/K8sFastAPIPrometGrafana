import logging
from fastapi import APIRouter, Depends, Request
from fastapi_jwt_auth import AuthJWT

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
    logging.info(f"Received code: {code}")
    return await service.yandex_callback(code, Authorize)
