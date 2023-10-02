from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Port
from app.schemas.port_schemas import PortSchemas


class CRUDPort(CRUDBase[Port, PortSchemas, PortSchemas]):
    port_mapping = {"ystad": "sweden", "swinoujscie": "poland"}

    async def get_port_by_id(self, port_id: int, db: AsyncSession) -> "Port" | None:
        if port_id:
            query = select(
                self.model.id,
                self.model.name,
                self.model.country_id,
            ).where(self.model.id == port_id)
            port = await db.execute(query)
            return port.one_or_none()

    async def get_ports_by_country_id(self, country_id: int, db: AsyncSession) -> "Port" | None:
        query = select(
            self.model.id,
            self.model.name,
            self.model.country_id,
        ).where(self.model.country_id == country_id)
        port = await db.execute(query)
        return port.all()

    async def get_port_by_name(self, port_name: str, db: AsyncSession) -> "Port" | None:
        if port_name:
            query = select(
                self.model.id,
                self.model.name,
                self.model.country_id,
            ).where(self.model.name == port_name)
            port = await db.execute(query)
            return port.one_or_none()

    async def create_port(
        self,
        new_port: PortSchemas,
        db: AsyncSession,
    ) -> "Port":
        new_port_data = self.model(
            name=new_port.name,
            country_id=new_port.country_id,
        )
        db.add(new_port_data)
        await db.commit()
        await db.refresh(new_port_data)

        return new_port_data

    async def get_or_create_by_name(self, searching_port_name: str, country_id: int, db: AsyncSession) -> "Port":
        port = await self.get_port_by_name(searching_port_name, db)
        if port is None:
            port = await self.create_port(PortSchemas(name=searching_port_name, country_id=country_id), db)

        return port


port_crud = CRUDPort(model=Port)
