# SPDX-License-Identifier: AGPL-3.0-or-later
# app/core/database.py

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession,
    async_sessionmaker
)

from app.db.base import Base
from .config import get_settings


settings = get_settings()

engine = create_async_engine(settings.database_url, echo=True)

async_session_local = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """Check that the database connection is alive."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("SELECT 1"))

async def close_db():
    """Close the database engine gracefully."""
    await engine.dispose()

async def get_session():
    async with async_session_local() as session:
        yield session
