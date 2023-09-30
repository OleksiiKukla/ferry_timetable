from app.crud.base import CRUDBase
from app.models import Country
from app.schemas.country_schemas import CountrySchemas, CountryCreateSchemas
from typing import Generic, List, Type, TypeVar
from sqlalchemy import desc, select, update

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base


# FerryType = TypeVar("FerryType", bound=Base)
# PortType = TypeVar("PortType", bound=Base)

class CRUDCountry(CRUDBase[Country, CountryCreateSchemas, CountryCreateSchemas]):

    async def create_country(
            self,
            new_country_name: str,
            abbreviation: str,
            db: AsyncSession,
    ) -> Country:
        new_country_data = self.model(
            name=new_country_name,
            abbreviated_name=abbreviation,
        )
        db.add(new_country_data)
        await db.commit()
        await db.refresh(new_country_data)

        return new_country_data

    async def get_by_name(self, country_name: str, db: AsyncSession) -> Country | None:
        if country_name:
            query = (
                select(
                    self.model.id,
                    self.model.name,
                    self.model.abbreviated_name,
                )
                .where(self.model.name == country_name)
            )
            country = await db.execute(query)
            return country.one_or_none()

    async def get_or_create(self, country_name: str, abbreviation: str, db: AsyncSession) -> Country:
        country = await self.get_by_name(country_name, db)
        if country is None:
            country = await self.create_country(country_name, abbreviation, db)
        return country

country_crud = CRUDCountry(model=Country)