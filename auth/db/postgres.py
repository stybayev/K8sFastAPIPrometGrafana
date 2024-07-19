from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from auth.core.config import settings
from typing import AsyncGenerator
import httpx

Base = declarative_base()

engine = create_async_engine(settings.db.url, echo=settings.log_sql_queries, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        from auth.models.users import LoginHistory, Role, User, UserRole
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Генератор для получения httpx.AsyncClient
    """
    async with httpx.AsyncClient() as client:
        yield client
