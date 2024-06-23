from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text
from auth.core.config import settings

Base = declarative_base()

engine = create_async_engine(settings.db.url, echo=settings.log_sql_queries, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_database() -> None:
    print('Creating database...')
    async with engine.begin() as conn:
        print('Creating schema...')
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        print('Creating tables...')
        from auth.models.users import User, Role, UserRole, LoginHistory
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
