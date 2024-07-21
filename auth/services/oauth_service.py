import uuid
from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.core.config import settings
from auth.db.postgres import get_db_session, get_http_client
from auth.models.social import SocialAccount
from auth.schema.tokens import TokenResponse
from auth.schema.users import UserCreate
from auth.services.users import UserService, get_user_service
from auth.utils.enums import AuthProvider


class OAuthService:
    def __init__(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        client: httpx.AsyncClient,
    ):
        self.user_service = user_service
        self.db_session = db_session
        self.client = client

    async def login(self, provider: AuthProvider):
        """
        Создание URL для перенаправления пользователя на провайдера для авторизации
        """
        if provider == AuthProvider.YANDEX:
            redirect_uri = settings.oauth.redirect_uri
            client_id = settings.oauth.client_id
            auth_url = f"{settings.oauth.auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
            return {"auth_url": auth_url}

    async def get_token(self, provider: AuthProvider, code: str):
        """
        Получение токена от провайдера
        """
        if provider == AuthProvider.YANDEX:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.oauth.client_id,
                "client_secret": settings.oauth.client_secret,
                "redirect_uri": settings.oauth.redirect_uri,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = await self.client.post(
                settings.oauth.token_url, data=data, headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get access token",
                )
            return response.json()

    async def get_user_info(self, provider: AuthProvider, access_token: str):
        """
        Получение информации о пользователе от провайдера
        """
        if provider == AuthProvider.YANDEX:
            headers = {"Authorization": f"OAuth {access_token}"}
            response = await self.client.get(
                settings.oauth.user_info_url, headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info",
                )
            return response.json()

    async def get_or_create_user(self, user_info: dict):
        """
        Получение или создание пользователя на основе информации от провайдера
        """
        query = select(SocialAccount).filter_by(
            social_id=user_info.get("id"), social_name="yandex"
        )
        result = await self.db_session.execute(query)
        social_account = result.scalars().first()

        if social_account:
            user = await self.user_service.get_user_by_id(social_account.user_id)
        else:
            user = await self.user_service.get_user_by_universal_login(
                user_info.get("default_email")
            )
            if not user:
                user_data = UserCreate(
                    login=user_info.get("login"),
                    email=user_info.get("default_email"),
                    password="",
                    first_name=user_info.get("first_name"),
                    last_name=user_info.get("last_name"),
                )
                user = await self.user_service.create_user(
                    login=user_data.login,
                    email=user_data.email,
                    password=user_data.password,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                )
                social_account = SocialAccount(
                    user_id=user.id,
                    social_id=user_info.get("id"),
                    social_name="yandex",
                )
                self.db_session.add(social_account)
                await self.db_session.commit()

        return user

    async def generate_tokens_for_user(self, user, Authorize: AuthJWT):
        """
        Генерация токенов для пользователя
        """
        roles = await self.user_service.get_user_roles(user.id)
        user_claims = {
            "id": str(user.id),
            "roles": roles,
            "first_name": str(user.first_name),
            "last_name": str(user.last_name),
        }
        tokens = await self.user_service.token_service.generate_tokens(
            Authorize, user_claims, str(user.id)
        )
        return TokenResponse(
            access_token=tokens.access_token, refresh_token=tokens.refresh_token
        )

    async def callback(self, provider: AuthProvider, code: str, Authorize: AuthJWT):
        """
        Обработка кода авторизации провайдера, получение токена доступа и информации о пользователе
        """
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided",
            )

        token_response = await self.get_token(provider, code)
        access_token = token_response["access_token"]

        user_info = await self.get_user_info(provider, access_token)
        user = await self.get_or_create_user(user_info)

        return await self.generate_tokens_for_user(user, Authorize)

    async def unlink_social_account(self, user_id: uuid.UUID, social_name: str):
        """
        Удаление привязки аккаунта в соцсети от пользователя.
        """
        query = select(SocialAccount).filter_by(
            user_id=user_id, social_name=social_name
        )
        result = await self.db_session.execute(query)
        social_account = result.scalars().first()

        if not social_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Social account not found"
            )

        await self.db_session.delete(social_account)
        await self.db_session.commit()
        return {"detail": "Social account unlinked successfully"}


@lru_cache()
def get_oauth_service(
    user_service: UserService = Depends(get_user_service),
    db_session: AsyncSession = Depends(get_db_session),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> OAuthService:
    return OAuthService(user_service, db_session, client)
