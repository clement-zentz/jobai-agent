# SPDX-License-Identifier: AGPL-3.0-or-later
# tests/conftest.py
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from app.models.job_offer import Base

from app.core.database import get_session
from app.main import app


@pytest.fixture()
def event_loop():
    # needed for pytest-asyncio if using session-scoped fixtures
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def postgres_container():
    """
    Start a PostgreSQL test container once per test session.
    """
    container = PostgresContainer("postgres:16")
    container.start()
    yield container
    container.stop()


@pytest.fixture()
async def test_engine(postgres_container):
    """
    Create a dedicated async engine connected to the Postgre test container
    """
    raw_url = postgres_container.get_connection_url()
    url = make_url(raw_url)

    # Force async driver
    async_url = url.set(drivername="postgresql+asyncpg")

    engine = create_async_engine(async_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async session bound to the test engine.
    """
    async_session_maker = async_sessionmaker(
        test_engine, 
        expire_on_commit=False, 
        class_=AsyncSession
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def async_client(test_session: AsyncSession):
    """
    Override get_session to use the test session
    and return an AsyncClient for making async requests.
    """

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
