import uuid
import datetime

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from functools import lru_cache
from typing import Optional, List
from fastapi import Depends, HTTPException, status

from auth.core.config import settings
from auth.db.postgres import get_db_session
from auth.db.redis import get_redis
from auth.models.users import User, UserRole, Role
from auth.schema.tokens import TokenResponse
from fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from werkzeug.security import generate_password_hash
from fastapi_jwt_auth.exceptions import AuthJWTException


class UserService:
    def __init__(self, db_session: AsyncSession, redis: Redis):
        self.db_session = db_session
        self.redis = redis

    async def get_by_login(self, login: str) -> Optional[User]:
        """
        Поиск пользователя по логину
        """
        result = await self.db_session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()

    async def create_user(self, login: str, password: str, first_name: Optional[str] = None,
                          last_name: Optional[str] = None) -> User:
        """
        Создание пользователя
        """
        new_user = User(login=login, password=password, first_name=first_name, last_name=last_name)
        self.db_session.add(new_user)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Login already registered')

    async def get_user_roles(self, user_id: uuid.UUID) -> List[str]:
        """
        Получение ролей пользователя из БД.
        """
        result = await self.db_session.execute(
            select(Role.name).
            join(UserRole, Role.id == UserRole.role_id).
            where(UserRole.user_id == user_id)
        )
        roles = result.scalars().all()
        return roles

    async def login(self, login: str, password: str, Authorize: AuthJWT) -> TokenResponse:
        """
        Вход пользователя
        """
        db_user = await self.get_by_login(login)
        if not db_user or not db_user.check_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid login or password')

        roles = await self.get_user_roles(db_user.id)
        user_claims = {'id': str(db_user.id), 'roles': roles}
        return await self.generate_tokens(Authorize, user_claims, db_user.id)

    async def update_user_credentials(self, user_id: uuid.UUID, login: Optional[str] = None,
                                      password: Optional[str] = None) -> User:
        """
        Обновление логина или пароля пользователя
        """
        user = await self.db_session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        if login:
            user.login = login
        if password:
            user.password = generate_password_hash(password)

        try:
            await self.db_session.commit()
            await self.db_session.refresh(user)
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Login already registered')

        return user

    async def refresh_access_token(self, authorize: AuthJWT) -> TokenResponse:
        """
        Получение новой пары токенов Access и Refresh
        """
        # проверяем токен
        try:
            authorize.jwt_refresh_token_required()
        except AuthJWTException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        raw_jwt = authorize.get_raw_jwt()
        user_id = raw_jwt['jti']
        not_unique_token = await self.redis.get(f'refresh_token:{raw_jwt["jti"]}')
        # проверка на одноразовость
        if not_unique_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token already used. Need use other refresh token."
            )
        # проверка, нет ли токена в невалидных
        invalid_token = await self.redis.get(f"invalid_token:{user_id}")
        if invalid_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
        roles = await self.get_user_roles(uuid.UUID(user_id))
        user_claims = {'id': user_id, 'roles': roles}

        await self.redis.delete(f"refresh_token:{raw_jwt['jti']}")
        await self.redis.set(f"invalid_token:{raw_jwt['jti']}", user_id)
        return await self.generate_tokens(authorize, user_claims, user_id)

    async def generate_tokens(
            self,
            authorize: AuthJWT,
            claims: dict,
            user_id: str
    ) -> TokenResponse:
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


@lru_cache()
def get_user_service(db_session: AsyncSession = Depends(get_db_session),
                     redis: Redis = Depends(get_redis)) -> UserService:
    return UserService(db_session, redis)
