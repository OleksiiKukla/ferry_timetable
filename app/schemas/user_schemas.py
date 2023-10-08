import enum
from datetime import datetime

from app.schemas.base import DBBase


class UserSchemas(DBBase):
    id: int
    chat_id: int
    name: str
    created_date: datetime
    last_request: datetime
    language: str | None


class UserCreateSchemas(DBBase):
    chat_id: int | None = None
    name: str
    language: enum.Enum | None = None
