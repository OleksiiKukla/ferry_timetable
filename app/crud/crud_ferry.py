import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Ferry, Owner
from app.schemas.ferry_schemas import FerryCreateSchemas

# FerryType = TypeVar("FerryType", bound=Base)
# PortType = TypeVar("PortType", bound=Base)


class CRUDFerry(CRUDBase[Ferry, FerryCreateSchemas, FerryCreateSchemas]):
    async def create_ferry(
        self,
        new_ferry: FerryCreateSchemas,
        db: AsyncSession,
    ) -> "Ferry":
        new_ferry_data = self.model(
            name=new_ferry.name,
            date=new_ferry.date,
            time_departure=new_ferry.time_departure,
            time_arrival=new_ferry.time_arrival,
            port_departure_id=new_ferry.port_departure_id,
            port_arrival_id=new_ferry.port_arrival_id,
        )
        db.add(new_ferry_data)
        await db.commit()
        await db.refresh(new_ferry_data)

        return new_ferry_data

    async def get_ferries(
        self,
        db: AsyncSession,
        date: datetime.datetime | None = None,
        port_departure_id: int | None = None,
        port_arrival_id: int | None = None,
    ) -> list["Ferry"]:
        query = select(
            self.model.id,
            self.model.name,
            self.model.date,
            self.model.time_departure,
            self.model.time_arrival,
            self.model.port_departure_id,
            self.model.port_arrival_id,
            self.model.owner_id,
        ).where(
            self.model.port_departure_id == port_departure_id,
            self.model.port_arrival_id == port_arrival_id,
            self.model.date == date.date(),
        )
        ferries = await db.execute(query)
        return ferries.all()

    async def get_all(
        self,
        db: AsyncSession,
    ) -> list["Ferry"]:
        query = select(
            self.model.id,
            self.model.name,
            self.model.date,
            self.model.time_departure,
            self.model.time_arrival,
            self.model.port_departure_id,
            self.model.port_arrival_id,
            self.model.owner_id,
        )
        ferries = await db.execute(query)
        return ferries.all()

    async def change_owner(
        self,
        db: AsyncSession,
        ferry_id:int,
        owner_id: int,
    ) -> "Ferry":
        query = (
            update(self.model)
            .where(self.model.id == ferry_id)
            .values(owner_id=owner_id)
            .returning(self.model)
        )
        result = await db.execute(query)
        updated_card = result.one_or_none()
        await db.commit()
        return updated_card

ferry_crud = CRUDFerry(model=Ferry)
