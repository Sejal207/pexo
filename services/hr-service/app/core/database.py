from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

schema = settings.DB_SCHEMA if settings.DB_SCHEMA and settings.DB_SCHEMA != "public" else None
metadata = MetaData(schema=schema)


class Base(DeclarativeBase):
    metadata = metadata


engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
