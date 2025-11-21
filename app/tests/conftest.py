# tests/conftest.py
import asyncio
import pytest
import time
from typing import AsyncGenerator
from testcontainers.postgres import PostgresContainer
from testcontainers.core.waiting_utils import WaitStrategy, WaitStrategyTarget
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_session
from sqlalchemy.engine.url import make_url


# class LogWaitStrategy(WaitStrategy):
#     def __init__(self, phrase: str, timeout: int = 30):
#         self.phrase = phrase
#         self.timeout = timeout

#     def wait_until_ready(self, target: WaitStrategyTarget):
#         start = time.time()

#         # Correct API for your Testcontainers version:
#         for line in target.get_logs():
#             decoded = line.decode("utf-8", errors="ignore")
#             if self.phrase in decoded:
#                 return

#             if time.time() - start > self.timeout:
#                 raise TimeoutError(
#                     f"Timeout waiting for log message: {self.phrase}"
#                 )


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
    # container = (
    #     PostgresContainer("postgres:16")
    #     .waiting_for(LogWaitStrategy("database system is ready to accept connections"))
    # )
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
        await conn.run_sync(SQLModel.metadata.create_all)

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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


