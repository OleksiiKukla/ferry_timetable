import datetime

import sqlalchemy as sa
from app.db.session import Base
from sqlalchemy.orm import relationship

class Port(Base):
    __tablename__ = 'ports'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name: str = sa.Column(sa.String)
    country_id: int = sa.Column(sa.Integer, sa.ForeignKey("countries.id"))

    countries = relationship('Country', back_populates='ports')
    ferries = relationship('Ferry', secondary='port_ferry', back_populates='ports')
