import datetime

from app.schemas.base import DBBase


class FerrySchemas(DBBase):

    id: int
    name: str
    date: str
    time_departure: str
    time_arrival: str
    port_departure_id: int
    port_arrival_id: int


class FerryCreateSchemas(DBBase):

    name: str
    date: datetime.datetime
    time_departure: str
    time_arrival: str
    port_departure_id: int
    port_arrival_id: int


class FerryGetSchemas(DBBase):

    name: str
    date: datetime.datetime
    time_departure: str
    time_arrival: str
    port_departure_id: int
    port_arrival_id: int
