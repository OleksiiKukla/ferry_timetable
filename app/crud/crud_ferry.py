import datetime
from sqlalchemy import desc, select, update

from app.crud.base import CRUDBase
from app.models import Ferry
from app.schemas.ferry_schemas import FerryCreateSchemas
from typing import Generic, List, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base


# FerryType = TypeVar("FerryType", bound=Base)
# PortType = TypeVar("PortType", bound=Base)

class CRUDFerry(CRUDBase[Ferry, FerryCreateSchemas, FerryCreateSchemas]):


    async def create_ferry(
            self,
            new_ferry: FerryCreateSchemas,
            db: AsyncSession,
    ) -> Ferry:
        new_ferry_data = self.model(
            name=new_ferry.name,
            date = new_ferry.date,
            time_departure = new_ferry.time_departure,
            time_arrival = new_ferry.time_arrival,
            port_departure_id = new_ferry.port_departure_id,
            port_arrival_id = new_ferry.port_arrival_id,
        )
        db.add(new_ferry_data)
        await db.commit()
        await db.refresh(new_ferry_data)

        return new_ferry_data

    async def get_ferries(self, db: AsyncSession, date: datetime.datetime | None = None, port_departure_id: int | None = None, port_arrival_id: int | None = None):
        query = (select(
            self.model.id,
            self.model.name,
            self.model.date,
            self.model.time_departure,
            self.model.time_arrival,
        )
        .where(self.model.port_departure_id == port_departure_id, self.model.port_arrival_id == port_arrival_id, self.model.date == date.date()))
        ferries = await db.execute(query)
        return ferries.all()


ferry_crud = CRUDFerry(model=Ferry)