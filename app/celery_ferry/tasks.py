import asyncio
import logging

from app.db.session import get_or_create_session
from app.timetable.parser import Parser

from .worker import app

logger = logging.getLogger(__name__)


@app.task(name="parse_polferries")
def parse_polferries() -> None:
    asyncio.get_event_loop().run_until_complete(_parse_polferries())


async def _parse_polferries() -> None:
    session = get_or_create_session()
    parser = Parser()
    await parser.parser_polferries(session)
    await session.close()

    logger.info("Polferries parsed.")
