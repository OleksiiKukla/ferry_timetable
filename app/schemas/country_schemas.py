from app.schemas.base import DBBase


class CountrySchemas(DBBase):

    id: int
    name: str
    abbreviated_name: str | None = None


class CountryCreateSchemas(DBBase):
    name: str
    abbreviated_name: str | None = None
