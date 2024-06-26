import datetime
from fastapi_jwt_auth import AuthJWT
from auth.core.config import settings
from auth.schema.tokens import TokenResponse
from redis.asyncio import Redis
from uuid import UUID


class TokenService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def generate_tokens(self, authorize: AuthJWT, claims: dict, user_id: str) -> TokenResponse:
        """
        Процедура генерации пары токенов
        """
        access_token = authorize.create_access_token(
            subject=str(user_id),
            user_claims=claims,
            fresh=True,
            expires_time=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES)
        )
        refresh_token = authorize.create_refresh_token(
            subject=str(user_id),
            expires_time=datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES)
        )

        await self.redis.set(
            f'access_token:{access_token}',
            str(user_id),
            ex=settings.ACCESS_TOKEN_EXPIRES * 60
        )
        await self.redis.set(
            f'refresh_token:{refresh_token}',
            str(user_id),
            ex=settings.REFRESH_TOKEN_EXPIRES * 60
        )

        return TokenResponse(refresh_token=refresh_token, access_token=access_token)

    async def add_access_refresh_to_invalid(self, jti: str, user_id: UUID):
        """
        Добавление Access и Refresh токенов в невалидные
        """
        await self.redis.set(f"invalid_token:{jti}", str(user_id))
