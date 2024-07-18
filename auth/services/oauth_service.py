from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.models.social import SocialAccount
from auth.schema.tokens import TokenResponse
from auth.schema.users import UserCreate
from auth.services.users import UserService, get_user_service
from auth.db.postgres import get_db_session, get_http_client
from auth.core.config import settings


class OAuthService:
    def __init__(self, user_service: UserService, db_session: AsyncSession, client: httpx.AsyncClient):
        self.user_service = user_service
        self.db_session = db_session
        self.client = client

    async def yandex_login(self):
        """
        Создание URL для перенаправления пользователя на Яндекс для авторизации
        """
        redirect_uri = settings.oauth.redirect_uri
        client_id = settings.oauth.client_id
        auth_url = f"{settings.oauth.auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
        return {"auth_url": auth_url}

    async def yandex_callback(self, code: str, Authorize: AuthJWT):
        """
        Обработка кода авторизации Яндекса, получение токена доступа и информации о пользователе
        """
        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code not provided")

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.oauth.client_id,
            'client_secret': settings.oauth.client_secret,
            'redirect_uri': settings.oauth.redirect_uri
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Запрос для получения токена
        response = await self.client.post(settings.oauth.token_url, data=data, headers=headers)
        response_data = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get access token")

        # Запрос для получения информации о пользователе
        access_token = response_data['access_token']
        user_info_response = await self.client.get(settings.oauth.user_info_url,
                                                   headers={"Authorization": f"OAuth {access_token}"})
        user_info = user_info_response.json()

        if user_info_response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get user info")

        # Проверка, существует ли запись в SocialAccount
        query = select(SocialAccount).filter_by(social_id=user_info.get("id"), social_name="yandex")
        result = await self.db_session.execute(query)
        social_account = result.scalars().first()

        if social_account:
            # Если запись существует, получаем пользователя по user_id
            user = await self.user_service.get_user_by_id(social_account.user_id)
        else:
            # Если записи нет, создаем нового пользователя
            user = await self.user_service.get_user_by_universal_login(user_info.get("default_email"))
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
                    last_name=user_data.last_name
                )

            # Создаем новую запись в SocialAccount
            social_account = SocialAccount(
                user_id=user.id,
                social_id=user_info.get("id"),
                social_name="yandex"
            )
            self.db_session.add(social_account)
            await self.db_session.commit()

        # Генерация токенов для пользователя
        roles = await self.user_service.get_user_roles(user.id)
        user_claims = {"id": str(user.id),
                       "roles": roles,
                       "first_name": str(user.first_name),
                       "last_name": str(user.last_name)}
        tokens = await self.user_service.token_service.generate_tokens(Authorize, user_claims, str(user.id))

        return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@lru_cache()
def get_oauth_service(
        user_service: UserService = Depends(get_user_service),
        db_session: AsyncSession = Depends(get_db_session),
        client: httpx.AsyncClient = Depends(get_http_client)
) -> OAuthService:
    return OAuthService(user_service, db_session, client)
