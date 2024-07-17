import datetime
import uuid
from uuid import UUID

from fastapi_jwt_auth import AuthJWT
from opentelemetry import trace
from redis.asyncio import Redis

from auth.core.config import settings
from auth.core.tracer import traced
from auth.schema.tokens import TokenResponse

tracer = trace.get_tracer(__name__)


class TokenService:
    def __init__(self, redis: Redis):
        self.redis = redis

    @traced(__name__)
    async def generate_tokens(self, authorize: AuthJWT, claims: dict, user_id: str) -> TokenResponse:
        """
        Процедура генерации пары токенов
        """
        access_jti = str(uuid.uuid4())
        access_token = authorize.create_access_token(
            subject=str(user_id),
            user_claims={**claims, 'jti': access_jti},
            fresh=True,
            expires_time=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES)
        )
        refresh_jti = str(uuid.uuid4())
        refresh_token = authorize.create_refresh_token(
            subject=str(user_id),
            user_claims={'access_jti': access_jti, 'jti': refresh_jti},
            expires_time=datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES)
        )
        with tracer.start_as_current_span("set_access_token_redis_request"):
            await self.redis.set(
                f'access_token:{access_jti}',
                str(user_id),
                ex=settings.ACCESS_TOKEN_EXPIRES * 60
            )
        with tracer.start_as_current_span("set_refresh_token_redis_request"):
            await self.redis.set(
                f'refresh_token:{refresh_jti}',
                str(user_id),
                ex=settings.REFRESH_TOKEN_EXPIRES * 60
            )

        return TokenResponse(refresh_token=refresh_token, access_token=access_token)

    @traced(__name__)
    async def add_tokens_to_invalid(self, access_jti: str, refresh_jti: str, user_id: UUID):
        """
        Добавление Access и Refresh токенов в невалидные
        """
        with tracer.start_as_current_span("set_access_token_redis_request"):
            await self.redis.set(f"invalid_token:{access_jti}", str(user_id))
        with tracer.start_as_current_span("set_refresh_token_redis_request"):
            await self.redis.set(f"invalid_token:{refresh_jti}", str(user_id))
