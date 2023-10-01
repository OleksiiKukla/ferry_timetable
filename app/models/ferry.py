import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.session import Base


class Ferry(Base):
    __tablename__ = "ferries"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))
    date = sa.Column(sa.Date)
    time_departure = sa.Column(sa.String(30))
    time_arrival = sa.Column(sa.String(30))
    port_departure_id = sa.Column(sa.Integer, sa.ForeignKey("ports.id"))
    port_arrival_id = sa.Column(sa.Integer, sa.ForeignKey("ports.id"))

    ports = relationship("Port", secondary="port_ferry", back_populates="ferries")


class PortFerry(Base):
    __tablename__ = "port_ferry"

    id = sa.Column(sa.Integer, primary_key=True)
    port_id = sa.Column(sa.Integer, sa.ForeignKey("ports.id"))
    ferry_id = sa.Column(sa.Integer, sa.ForeignKey("ferries.id"))
