from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

schema = settings.DB_SCHEMA if settings.DB_SCHEMA and settings.DB_SCHEMA != "public" else None
metadata = MetaData(schema=schema)


class Base(DeclarativeBase):
    metadata = metadata


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # Neon closes idle pooled connections server-side; without pre_ping,
    # SQLAlchemy hands out a dead connection and the next query fails with
    # "connection is closed" instead of transparently reconnecting.
    pool_pre_ping=True,
    pool_recycle=300,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
