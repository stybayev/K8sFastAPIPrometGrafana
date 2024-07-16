from sqlalchemy.ext.asyncio import AsyncSession
from auth.models.users import User
from auth.db.postgres import get_db_session
from sqlalchemy.future import select


class OAuthService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_or_create_user(self, user_info: dict):
        # Пример для Yandex
        email = user_info.get('default_email')
        existing_user = await self.db_session.execute(select(User).where(User.login == email))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user:
            return existing_user

        new_user = User(
            login=email,
            password='',  # или сгенерируйте случайный парольOperation
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name')
        )
        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user
