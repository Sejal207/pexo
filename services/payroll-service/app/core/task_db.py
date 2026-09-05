"""
A separate engine for Celery tasks, deliberately not the FastAPI process's
module-level `app.core.database.engine`. asyncpg connections are bound to
the event loop that created them; a sync Celery task wraps its work in a
fresh `asyncio.run(...)` per invocation (a fresh event loop each time), so
reusing a pooled connection across invocations would hand a later loop a
connection opened by an earlier, already-closed one. NullPool sidesteps this
by never holding a connection open between checkouts.
"""
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

_task_engine = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
TaskSessionLocal = async_sessionmaker(_task_engine, class_=AsyncSession, expire_on_commit=False)
