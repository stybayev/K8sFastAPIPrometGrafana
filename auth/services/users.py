from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from functools import lru_cache
from typing import Optional
from fastapi import Depends, HTTPException, status
from auth.db.postgres import get_db_session
from auth.models.users import User
from fastapi_jwt_auth import AuthJWT


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login already registered")

    async def login(self, login: str, password: str, Authorize: AuthJWT) -> dict:
        """
        Вход пользователя
        """
        db_user = await self.get_by_login(login)
        if not db_user or not db_user.check_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")

        access_token = Authorize.create_access_token(subject=login)
        refresh_token = Authorize.create_refresh_token(subject=login)
        return {"access_token": access_token, "refresh_token": refresh_token}


@lru_cache()
def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db_session)
