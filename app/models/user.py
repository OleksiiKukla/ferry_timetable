import datetime

import sqlalchemy as sa

from app.db.session import Base
from app.schemas.enums import Languages


class User(Base):
    __tablename__ = "users"

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    chat_id: int = sa.Column(sa.Integer)
    name: str = sa.Column(sa.String)
    created_date: datetime.datetime = sa.Column(sa.DateTime, server_default=sa.func.now())
    last_request: datetime.datetime = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    language = sa.Column(sa.Enum(Languages), nullable=False, default=Languages.ENGLISH.value)
