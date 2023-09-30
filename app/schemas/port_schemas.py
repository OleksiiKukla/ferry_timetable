from app.schemas.base import DBBase


class PortSchemas(DBBase):
    name: str
    country_id: int
