# SPDX-License-Identifier: AGPL-3.0-or-later
# app/core/database.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from .config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=True)
async_session_local = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db():
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        yield session
