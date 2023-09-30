import sqlalchemy as sa
from app.db.session import Base
from sqlalchemy.orm import relationship


class Country(Base):
    __tablename__ = 'countries'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(sa.String)
    abbreviated_name: str = sa.Column(sa.String)

    ports = relationship('Port', back_populates='countries')