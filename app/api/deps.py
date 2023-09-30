from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_or_create_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        db = get_or_create_session()
        yield db
    finally:
        await db.close()
