import asyncio
import datetime
from decimal import Decimal
from typing import AsyncGenerator

import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import app.models as models
from app.api.deps import get_db
from app.core.config import settings
from app.db.session import Base
from app.main import app

load_dotenv()

test_db = settings.SQLALCHEMY_TEST_DATABASE_URI

engine = create_async_engine(test_db, poolclass=NullPool)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = test_db


async def override_get_async_session():
    async with async_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_async_session


@pytest_asyncio.fixture(autouse=True, scope="function")
async def prepare_database() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
