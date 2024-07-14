import uuid
from functools import lru_cache
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash

from auth.db.postgres import get_db_session
from auth.db.redis import get_redis
from auth.models.users import LoginHistory, Role, User, UserRole
from auth.schema.tokens import TokenResponse
from auth.schema.users import LoginHistoryResponse
from auth.services.tokens import TokenService
from auth.utils.permissions import access_token_required, refresh_token_required


class UserService:
    def __init__(
        self,
        db_session: AsyncSession,
        redis: Redis,
        token_service: TokenService,
    ):
        self.db_session = db_session
        self.redis = (redis,)
        self.token_service = token_service

    async def get_by_login(self, login: str) -> Optional[User]:
        """
        Поиск пользователя по логину
        """
        result = await self.db_session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()

    async def create_user(
        self,
        login: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """
        Создание пользователя
        """
        new_user = User(
            login=login,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.db_session.add(new_user)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already registered",
            )

    async def get_user_roles(self, user_id: uuid.UUID) -> List[str]:
        """
        Получение ролей пользователя из БД.
        """
        result = await self.db_session.execute(
            select(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id),
        )
        roles = result.scalars().all()
        return roles

    async def login(
        self,
        login: str,
        password: str,
        Authorize: AuthJWT,
        user_agent: str,
    ) -> TokenResponse:
        """
        Вход пользователя
        """
        db_user = await self.get_by_login(login)
        if not db_user or not db_user.check_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login or password",
            )

        roles = await self.get_user_roles(db_user.id)
        user_claims = {"id": str(db_user.id),
                       "roles": roles,
                       "first_name": str(db_user.first_name),
                       "last_name": str(db_user.last_name)}
        self.db_session.add(
            LoginHistory(user_id=db_user.id, user_agent=user_agent),
        )
        await self.db_session.commit()

        return await self.token_service.generate_tokens(
            Authorize,
            user_claims,
            db_user.id,
        )

    async def update_user_credentials(
        self,
        user_id: uuid.UUID,
        login: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """
        Обновление логина или пароля пользователя
        """
        user = await self.db_session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if login:
            user.login = login
        if password:
            user.password = generate_password_hash(password)

        try:
            await self.db_session.commit()
            await self.db_session.refresh(user)
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already registered",
            )

        return user

    @refresh_token_required
    async def logout_user(self, authorize: AuthJWT) -> bool:
        """
        Выход пользователя из аккаунта
        """

        raw_jwt = authorize.get_raw_jwt()
        user_id = raw_jwt["sub"]
        refresh_jti = raw_jwt["jti"]
        access_jti = raw_jwt["access_jti"]

        await self.token_service.add_tokens_to_invalid(access_jti, refresh_jti, user_id)
        return True

    @refresh_token_required
    async def refresh_access_token(self, authorize: AuthJWT) -> TokenResponse:
        """
        Получение новой пары токенов Access и Refresh
        """
        try:
            authorize.jwt_refresh_token_required()
        except AuthJWTException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        raw_jwt = authorize.get_raw_jwt()
        user_id = raw_jwt["sub"]

        roles = await self.get_user_roles(uuid.UUID(user_id))
        user_claims = {"id": user_id, "roles": roles}

        await self.token_service.add_tokens_to_invalid(
            raw_jwt["access_jti"],
            raw_jwt["jti"],
            user_id,
        )
        return await self.token_service.generate_tokens(authorize, user_claims, user_id)

    @access_token_required
    async def get_login_history(
        self,
        authorize: AuthJWT,
        page_size: int,
        page_number: int,
    ) -> List[LoginHistoryResponse]:
        user_id = uuid.UUID(authorize.get_jwt_subject())
        offset = (page_number - 1) * page_size

        result = await self.db_session.execute(
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.login_time.desc())
            .limit(page_size)
            .offset(offset),
        )
        history = result.scalars().all()
        return [
            LoginHistoryResponse(
                user_agent=h.user_agent,
                login_time=h.login_time,
            )
            for h in history
        ]


@lru_cache()
def get_user_service(
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> UserService:
    token_service = TokenService(redis)
    return UserService(db_session, redis, token_service)
