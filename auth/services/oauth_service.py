from sqlalchemy.ext.asyncio import AsyncSession
from auth.models.users import User
from auth.db.postgres import get_db_session
from sqlalchemy.future import select


class OAuthService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        pass
