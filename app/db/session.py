from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import app.core.config

Base = declarative_base()

__engine = None

__async_session = None


def get_or_create_engine() -> Engine:
    global __engine
    if not __engine:
        __engine = create_async_engine(app.core.config.settings.SQLALCHEMY_DATABASE_URI, future=True)
    return __engine


def get_or_create_session() -> AsyncSession:
    global __async_session
    if not __async_session:
        __async_session = sessionmaker(__engine, expire_on_commit=False, class_=AsyncSession)
    return __async_session()


async def dispose_engine():
    global __engine
    if __engine:
        await __engine.dispose()
    __engine = None
