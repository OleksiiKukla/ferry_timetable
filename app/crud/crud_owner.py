from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Owner
from app.schemas.owner_schemas import OwnerSchemas


class CRUDOwner(CRUDBase[Owner, OwnerSchemas, OwnerSchemas]):

    async def create_owner(
        self,
        name: str,
        db: AsyncSession,
    ) -> Owner:
        new_owner_data = self.model(
            name=name,
        )
        db.add(new_owner_data)
        await db.commit()
        await db.refresh(new_owner_data)

        return new_owner_data

    async def get_owner_by_name(self, name: str, db: AsyncSession) -> "Owner" | None:
        query = select(
            self.model.id,
            self.model.name,
        ).where(self.model.name == name)
        owner = await db.execute(query)
        return owner.one_or_none()

    async def get_or_create(
        self,
        name: str,
        db: AsyncSession,
    ) -> tuple[Owner, bool]:

        created = False
        user = await self.get_owner_by_name(db=db, name=name)

        if user is None:
            user = await self.create_owner(name=name, db=db)
            created = True
        return user, created



owner_crud = CRUDOwner(model=Owner)