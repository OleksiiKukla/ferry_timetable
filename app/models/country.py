import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.session import Base


class Country(Base):
    __tablename__ = "countries"

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(sa.String)
    abbreviated_name: str = sa.Column(sa.String)

    ports = relationship("Port", back_populates="countries")
