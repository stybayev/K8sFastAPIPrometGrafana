from select import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from functools import lru_cache
from typing import Optional
from fastapi import Depends, HTTPException, status
from auth.db.postgres import get_db_session
from auth.models.users import User


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


@lru_cache()
def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db_session)
